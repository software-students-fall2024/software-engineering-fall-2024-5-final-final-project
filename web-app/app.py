""" 
Web app frontend
"""

from flask import Flask, render_template
import os
from pymongo.mongo_client import MongoClient

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['theonepiece']
app = Flask(__name__)


@app.route("/")
def home():
    """Render main page"""
    return render_template("main.html")


# write new functions here
if __name__ == "__main__":
    app.run(debug=True, port=8080)
