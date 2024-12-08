from transformers import pipeline
from flask import Flask, request, jsonify


# Initialize Flask app
app = Flask(__name__)

# get the machine-learning classifier
# We used a pretrained model from https://huggingface.co/bhadresh-savani/distilbert-base-uncased-emotion 
classifier = pipeline("text-classification",model='bhadresh-savani/distilbert-base-uncased-emotion', return_all_scores=True)

#test prediction
prediction = classifier("I love using transformers. The best part is wide range of support and its easy to use", )
print(prediction)


from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze the journal entry text and return the top emotion and a list of scores for each emotion.
    """
    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "Invalid request"}), 400

    text = data["text"]
    try:
        # Run the prediction
        predictions = classifier(text)

        # Flatten the list if necessary (depends on classifier output structure)
        emotions = predictions[0] if isinstance(predictions, list) and len(predictions) > 0 else predictions

        # Extract the emotion with the highest score
        top_emotion = max(emotions, key=lambda x: x['score'])

        # Prepare response
        response = {
            "top_emotion": {
                "label": top_emotion["label"],
                "score": top_emotion["score"]
            },
            "all_emotions": emotions
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
