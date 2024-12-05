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



@app.route("/ml_analysis", methods=["POST"])
def ml_analysis():
    print("FUnction not completed....")
    return