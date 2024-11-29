"""
Module for performing sentiment analysis, topic modeling, emotion detection,
text summarization, and sentiment trend analysis on textual data retrieved
from a MongoDB collection.
"""

import os
import time
from collections import defaultdict
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

from gensim import corpora, models
from gensim.models import CoherenceModel
from gensim.models.phrases import Phrases, Phraser

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import text2emotion as te

import spacy

# step 1: retrive the data in this structure
# {
#     "_id": ObjectId("..."),
#     "request_id": "unique_request_id",
#     "sentences": [
#         {
#             "sentence": "Sentence 1.",
#             "status": "pending",
#             "analysis": null
#         },
#         {
#             "sentence": "Sentence 2.",
#             "status": "pending",
#             "analysis": null
#         },
#         // ... more sentences
#     ],
#     "overall_status": "pending",   // Indicates the status of the entire submission
#     "timestamp": ISODate("...")    // Timestamp of the submission
# }

# step 2: do analysis and store Compond, Neutural, Postive, and Negative metircs into analysis field
# step 3: do Topic Modeling, Emotion Detection, Text Summarization, Sentiment Trend Analysis

load_dotenv()

# MongoDB setup
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["sentiment"]
texts_collection = db["texts"]

# download necessary NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")
nltk.download("vader_lexicon")

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

def perform_sentiment_analysis(sentences):
    """
    Perform sentiment analysis on each sentence in the list.
    Adds sentiment scores (compound, neutral, positive, negative) to each sentence entry.

    :param sentences: List of sentence entries
    :return: Updated list with sentiment scores and status set to 'processed'
    """
    analyzer = SentimentIntensityAnalyzer()

    def analyze_sentence(sentence_entry):
        if sentence_entry["status"] == "pending":
            sentiment_scores = analyzer.polarity_scores(sentence_entry["sentence"])
            return {
                # unpack dictionary: extracts all key-value pairs from that dictionary
                **sentence_entry,
                "analysis": sentiment_scores,
                "status": "processed",
            }
        return sentence_entry

    return list(map(analyze_sentence, sentences))


# topic modeling
def perform_topic_modeling(sentences, num_topics=5):
    """
    Perform topic modeling on the list of sentences.
    Identifies main topics using LDA with improved preprocessing.

    :param sentences: List of sentence entries
    :param num_topics: Number of topics to identify
    :return: List of identified topics
    :raises: ValueError
    """

    def preprocess(text):
        tokens = word_tokenize(text.lower())
        tokens = [
            WordNetLemmatizer().lemmatize(token) for token in tokens if token.isalnum()
        ]
        tokens = [token for token in tokens if token not in stopwords.words("english")]
        return tokens

    texts = list(
        map(preprocess, [sentence_entry["sentence"] for sentence_entry in sentences])
    )
    # Create bigrams
    bigram = Phrases(texts, min_count=5, threshold=100)
    bigram_mod = Phraser(bigram)
    texts = [bigram_mod[doc] for doc in texts]
    # Create dictionary and filter extremes
    dictionary = corpora.Dictionary(texts)
    # dictionary.filter_extremes(no_below=3, no_above=0.9)
    # Create corpus
    corpus = [dictionary.doc2bow(text) for text in texts]
    if len(dictionary) == 0:
        raise ValueError(
            "Cannot compute LDA over an empty collection (no terms). "
            "Adjust your sample data or filtering parameters."
        )
    actual_num_topics = min(num_topics, len(dictionary))
    if actual_num_topics < num_topics:
        print(
            f"Adjusted num_topics from {num_topics} to {actual_num_topics} "
            f"based on the dictionary size."
        )

        num_topics = actual_num_topics
    # Build LDA model
    lda_model = models.LdaModel(
        corpus,
        num_topics=num_topics,
        id2word=dictionary,
        passes=15,
        iterations=100,
        alpha="auto",
        eta="auto",
        random_state=42,
    )
    # skip coherence calculation in test environment
    if not os.getenv("TESTING"):
        try:
            coherence_model_lda = CoherenceModel(
                model=lda_model, texts=texts, dictionary=dictionary, coherence="c_v"
            )
            coherence_score = coherence_model_lda.get_coherence()
            print(f"Coherence Score: {coherence_score}")
        except ValueError as e:
            print(f"Skipping coherence calculation: {str(e)}")

    topics = lda_model.print_topics(num_words=4)
    return topics


# emotion detection
def perform_emotion_detection(sentences):
    """
    Detect emotions in each sentence using the text2emotion package.
    Adds an 'emotions' field to each sentence entry.

    :param sentences: List of sentence entries
    :return: Updated list of sentence entries with emotions detected
    """

    def detect_emotion(sentence_entry):
        if "analysis" in sentence_entry and sentence_entry["analysis"] is not None:
            text = sentence_entry["sentence"]
            emotions = te.get_emotion(text)
            # determin dominat emotion(s)
            if any(emotions.values()):
                max_value = max(emotions.values())
                dominant_emotions = [
                    emotion
                    for emotion, score in emotions.items()
                    if score == max_value and score > 0
                ]
            else:
                dominant_emotions = ["Neutral"]

            return {**sentence_entry, "emotions": dominant_emotions}
        return sentence_entry

    return list(map(detect_emotion, sentences))


# overall emotion detection
def perform_overall_emotion_detection(sentences):
    """
    Determine the overall dominant emotion(s) across all sentences.
    Adds an 'overall_emotions' field to the document.

    :param sentences: List of sentence entries
    :return: Overall emotions list
    """

    emotion_counter = defaultdict(int)
    for sentence in sentences:
        emotions = sentence.get("emotions", [])
        for emotion in emotions:
            emotion_counter[emotion] += 1

    if emotion_counter:
        max_count = max(emotion_counter.values())
        dominant_overall_emotions = [
            emotion for emotion, count in emotion_counter.items() if count == max_count
        ]
    else:
        dominant_overall_emotions = ["Neutral"]

    return dominant_overall_emotions


# text summarization
def perform_text_summarization(sentences, sentence_count=5):
    """
    Generate a summary of the text using LexRank summarizer.

    :param sentences: List of sentence entries
    :param sentence_count: Number of sentences in the summary
    :return: Summary string
    """
    full_text = " ".join(sentence["sentence"] for sentence in sentences)
    parser = PlaintextParser.from_string(full_text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, sentences_count=sentence_count)
    summary = " ".join(str(sentence) for sentence in summary_sentences)
    return summary


# sentiment trend analysis
def perform_sentiment_trend_analysis(sentences):
    """
    Analyze sentiment trend by tracking compound scores of each sentence.
    Returns a list of sentiment scores with sentence indices.

    :param sentences: List of sentence entries
    :return: List of dictionaries with sentence index and compound score
    """

    def extract_compound_score(idx_entry):
        index, sentence_entry = idx_entry
        compound_score = (
            sentence_entry["analysis"]["compound"]
            if sentence_entry.get("analysis")
            else 0
        )
        return {"sentence_index": index, "compound": compound_score}

    return list(map(extract_compound_score, enumerate(sentences)))


# process all
def process_document(document):
    sentences = document["sentences"]
    sentences = perform_sentiment_analysis(sentences)
    topics = perform_topic_modeling(sentences)
    sentences = perform_emotion_detection(sentences)
    sentences = perform_ner(sentences)  # Ensure this line is present
    summary = perform_text_summarization(sentences)
    sentiment_trend = perform_sentiment_trend_analysis(sentences)
    overall_emotions = perform_overall_emotion_detection(sentences)
    # update document
    updated_document = {
        **document,
        "sentences": sentences,
        "overall_status": "processed",
        "topics": topics,
        "summary": summary,
        "sentiment_trend": sentiment_trend,
        "overall_emotions": overall_emotions,
        "timestamp": datetime.now(),
    }
    return updated_document




# update to database
def update_document_in_db(document):
    """
    Update the processed document in MongoDB.

    :param document: Document to update
    """
    doc_id = document["_id"]
    texts_collection.update_one(
        {"_id": doc_id},
        {
            "$set": {
                "sentences": document["sentences"],
                "overall_status": document["overall_status"],
                "topics": document["topics"],
                "summary": document["summary"],
                "sentiment_trend": document["sentiment_trend"],
                "overall_emotions": document["overall_emotions"],
                "timestamp": document["timestamp"],
            }
        },
    )

# perform named entity recognition
def perform_ner(sentences):
    """
    Perform Named Entity Recognition on each sentence.
    Adds an 'entities' field to each sentence entry.

    :param sentences: List of sentence entries
    :return: Updated list with entities extracted
    """
    def extract_entities(sentence_entry):
        text = sentence_entry["sentence"]
        doc = nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        return {**sentence_entry, "entities": entities}

    return list(map(extract_entities, sentences))


def main():
    """
    Continuously check and process pending documents in the MongoDB collection.
    Processes each document, performs analyses, updates results in the database,
    and repeats after a delay.
    """
    while True:
        pending_documents = texts_collection.find({"overall_status": "pending"})
        for document in pending_documents:
            updated_document = process_document(document)
            update_document_in_db(updated_document)
            print(f"Processed document with request_id: {document['request_id']}")

        # Add a delay to avoid overwhelming the database
        time.sleep(5)


if __name__ == "__main__":
    main()
