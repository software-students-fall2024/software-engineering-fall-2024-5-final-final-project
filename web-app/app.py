"""
This module sets up a Flask application to handle routes and connect to MongoDB.
It uses environment variables for configuration.
"""

import os  # Standard library imports
from dotenv import load_dotenv  # For loading environment variables
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

load_dotenv()

app = Flask(__name__)
cxn = MongoClient(os.getenv("MONGO_URI"))
db = cxn[os.getenv("MONGO_DBNAME")]
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey123")


# User Class
class User(UserMixin):
    """
    User class that extends UserMixin for Flask-Login.

    Attributes:
        id (str): The user's unique ID.
        username (str): The user's username.
        password (str): The user's hashed password.
        gender(str): The user's gender
    """

    def __init__(self, user_id, username, password, gender):
        """
        Initialize the User object.

        Args:
            user_id (str): The user's unique ID.
            username (str): The user's username.
            password (str): The user's hashed password.
            gender(str): The user's gender
        """
        self.id = user_id
        self.username = username
        self.password = password
        self.gender  = gender

##########################################
# LOGIN MANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    """
    User loader callback for Flask-Login.

    Args:
        user_id (str): The user's unique ID.

    Returns:
        User: The User object if found, else None.
    """
    user_data = db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(
            user_id=str(user_data["_id"]),
            username=user_data["username"],
            password=user_data["password"],
            gender=user_data["gender"]
        )
    return None


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handle user registration.

    On GET request, renders the registration page.
    On POST request, processes the registration form and creates a new user.

    Returns:
        Response: Redirects to login page upon successful registration,
                  or renders registration page with error messages.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        repassword = request.form["repassword"]
        gender = request.form["gender"]
        
        if password != repassword:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)
        if db.users.find_one({"username": username}):
            flash("Username already exists.")
            return redirect(url_for("register"))

        # Insert new user into the database with gender
        db.users.insert_one({
            "username": username,
            "password": hashed_password,
            "gender": gender  # Save the gender
        })

        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.

    On GET request, renders the login page.
    On POST request, processes the login form and logs in the user.

    Returns:
        Response: Redirects to index page upon successful login,
                  or renders login page with error messages.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user_data = db.users.find_one({"username": username})

        if user_data and check_password_hash(user_data["password"], password):
            user = User(
                user_id=str(user_data["_id"]),
                username=user_data["username"],
                password=user_data["password"],
                gender=user_data["gender"]  # Add this line
            )
            login_user(user)
            flash("Login successful!")
            return redirect(url_for("index"))
        flash("Invalid username or password.")
        return redirect(url_for("login"))
    # Explicitly return a rendered template for GET requests
    return render_template("login.html")


# LOGOUT
@app.route("/logout")
@login_required
def logout():
    """
    Log out the current user and redirect to the login page.

    Returns:
        Response: Redirects to the login page with a logout message.
    """
    logout_user()
    session.pop("_flashes", None)
    flash("You have been logged out.")
    return redirect(url_for("login"))

@app.route('/')
@login_required
def index():
    city = "New York"  
    temperature, description = get_weather(city, API_KEY)

    if temperature is not None:
        temperature = int(temperature)
        outfit = get_outfit_from_db(temperature, current_user.gender)
        
        return render_template(
            'index.html',
            city=city,
            temperature=f"{temperature}°C",
            description=description,
            outfit_image=outfit["image"],
            outfit_description=outfit["description"]
        )
    else:
        return render_template(
            'index.html',
            city=city,
            temperature="N/A",
            description="Weather data unavailable",
            outfit_image="/images/default.png",
            outfit_description="No outfit found"
        )
      
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
API_KEY = os.getenv("OPENWEATHER_API_KEY")

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

def seed_database():
    categories = {
        "cold": {"min": -10, "max": 0},
        "cool": {"min": 1, "max": 15},
        "warm": {"min": 16, "max": 25},
        "hot": {"min": 26, "max": 40}
    }
    images_folder = "./images"
    outfit_data = []

    for category, temp_range in categories.items():
        category_folder = os.path.join(images_folder, category)
        if os.path.exists(category_folder):
            images = [
                img for img in os.listdir(category_folder) 
                if img.lower().endswith((".jpg", ".png"))
            ]
            for image in images:
                outfit_data.append({
                    "temperature_range": temp_range,
                    "weather_condition": category,
                    "image_url": f"/images/{category}/{image}" 
                })
        else:
            print(f"Folder for category '{category}' does not exist. Skipping...")

    if outfit_data:
        db.outfits.insert_many(outfit_data)
        print(f"Inserted {len(outfit_data)} entries into the database!")
    else:
        print("Failed to put pics in database")

def get_outfit_from_db(temp, gender="all"):
    # Query for matching temperature range and gender
    outfit = db.outfits.find_one({
        "temperature_range.min": {"$lte": temp},
        "temperature_range.max": {"$gte": temp},
        "gender": {"$in": [gender, "all"]}
    })
    if outfit:
        return {
            "image": outfit["image_url"],
            "description": f"Outfit for {gender.capitalize()} in this temperature range"
        }
    else:
        return {
            "image": "/images/default.png",
            "description": "Default Outfit"
        }


# Run the app
if __name__ == "__main__":
    seed_database() 
    FLASK_PORT = os.getenv("FLASK_PORT", "5000")
    app.run(debug=True)

