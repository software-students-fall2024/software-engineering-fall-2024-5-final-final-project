"""
This module sets up a Flask application to handle routes and connect to MongoDB.
It uses environment variables for configuration.
"""

import os  # Standard library imports
import subprocess
import uuid
from datetime import datetime
import logging
import requests
from flask import (
    Flask,
    render_template,
    jsonify,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from bson.objectid import ObjectId

app = Flask(__name__)

# Function to get weather data
def get_weather(city_name, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        return temperature, weather_description
    else:
        return None, None

# API key for OpenWeatherMap
API_KEY = "your_openweathermap_api_key"

# Flask route to fetch weather data
@app.route('/get_weather', methods=['GET'])
def fetch_weather():
    city = request.args.get('city', 'New York')  # Default city is New York
    temperature, description = get_weather(city, API_KEY)
    if temperature is not None:
        return jsonify({
            "city": city,
            "temperature": f"{temperature}°C",
            "description": description
        })
    else:
        return jsonify({"error": "Could not fetch weather data"}), 400

# Run the app
if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "11000")
    app = create_app()
    app.run(debug=True)
