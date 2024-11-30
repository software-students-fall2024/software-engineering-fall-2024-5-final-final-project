"""
This module implements a Flask web application for sentiment analysis.
It allows users to submit text, which is then split into sentences and stored in MongoDB.
Results can later be fetched if the analysis is complete.
"""

import uuid
from datetime import datetime
import os
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient, errors
import nltk
from nltk.tokenize import sent_tokenize
from collections import defaultdict

app = Flask(__name__)

# Download NLTK data for sentence tokenization
nltk.download("punkt")

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)  # Adjust the connection string if necessary
db = client["sentiment"]  # Database name
collection = db["texts"]  # Collection name


@app.route("/")
def index():
    """Render the index page."""
    return render_template("index.html")


@app.route("/checkSentiment", methods=["POST"])
def submit_sentence():
    """
    Process the input sentence, split into individual sentences,
    and store them in MongoDB with a unique request_id.
    """
    data = request.get_json()
    paragraph = data.get("sentence")

    # Split paragraph into individual sentences
    sentences = sent_tokenize(paragraph)

    # Generate a unique request_id
    request_id = str(uuid.uuid4())

    # Create sentence entries with status "pending" and analysis as null
    sentence_entries = [
        {"sentence": sentence, "status": "pending", "analysis": None}
        for sentence in sentences
    ]

    # Create the document structure
    document = {
        "request_id": request_id,
        "sentences": sentence_entries,
        "overall_status": "pending",
        "timestamp": datetime.now(),
    }

    try:
        # Insert into MongoDB
        result = collection.insert_one(document)
        print("Inserted Document ID:", result.inserted_id)  # Debugging line
    except errors.PyMongoError as e:
        print(f"Error inserting document: {e}")  # Specific error handling for MongoDB

    # Return the request_id for fetching results later
    return jsonify({"request_id": request_id})


@app.route("/get_analysis", methods=["GET"])
def get_analysis():
    """
    Fetch the sentiment analysis result for a given request_id.
    Only returns processed documents.
    """
    request_id = request.args.get("request_id")
    print(
        f"Received request to get analysis for request_id: {request_id}"
    )  # Debugging line

    document = collection.find_one(
        {"request_id": request_id, "overall_status": "processed"}
    )
    if document:
        print("Document found:", document)  # Debugging line
        document["_id"] = str(document["_id"])
        return jsonify(document)
    print("No processed analysis found for request_id:", request_id)  # Debugging line
    return jsonify({"message": "No processed analysis found"}), 404

@app.route("/emotion_intensity/<string:request_id>", methods=["GET"])
def get_emtion_intensity(request_id):
    """
    Calculate the intensity of each emotion for the given document and return the result as JSON.
    """
    document = collection.find_one({"request_id": request_id})

    if not document:
        return jsonify({"error": "Document not found"}), 404
    
    # caculate emotion intensity
    emotion_intensity = defaultdict(float)
    for sentence in document.get("sentences", []):
        emotions = sentence.get("emotions", [])
        for emotion in emotions:
            emotion_intensity[emotion] += 1
    
    # normalize the values by the total number of sentences to get average intensity
    total_sentences = len(document.get("sentences", []))
    if total_sentences > 0:
        emotion_intensity = {k: v / total_sentences for k, v in emotion_intensity.items()}

    return jsonify(emotion_intensity)

if __name__ == "__main__":
    app.run(debug=True)
