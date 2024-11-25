from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Initialize MongoDB
mongo = PyMongo(app)
db = mongo.db

# Models
def add_bar(bar_data):
    """Add a new bar to the database."""
    return db.bars.insert_one(bar_data)

def get_all_bars():
    """Fetch all bars from the database."""
    return list(db.bars.find())

def recommend_bars(preference):
    """
    Recommend bars based on user preferences.
    
    Parameters:
        preference: dict with user preferences (e.g., price, location, type)
    
    Returns:
        List of recommended bars.
    """
    query = {}
    
    if 'price' in preference:
        query['price'] = preference['price']
    if 'location' in preference:
        query['location'] = preference['location']
    if 'type' in preference:
        query['type'] = preference['type']
    
    return list(db.bars.find(query))

# Routes
@app.route("/add_bar", methods=["POST"])
def add_bar_route():
    """Add a new bar to the database."""
    data = request.get_json()
    result = add_bar(data)
    return jsonify({"success": True, "bar_id": str(result.inserted_id)}), 201

@app.route("/get_bars", methods=["GET"])
def get_bars():
    """Get all bars."""
    bars = get_all_bars()
    return jsonify(bars), 200

@app.route("/recommend", methods=["POST"])
def recommend():
    """Get bar recommendations based on preferences."""
    data = request.get_json()
    recommendations = recommend_bars(data)
    return jsonify(recommendations), 200

# Run the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
