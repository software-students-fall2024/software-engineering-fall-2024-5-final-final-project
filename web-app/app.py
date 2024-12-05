""" 
Web app frontend
"""

from flask import Flask, render_template
from flask_login import current_user, login_required
import os
from pymongo.mongo_client import MongoClient
from user.auth import auth, login_manager

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['theonepiece']

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client['theonepiece']
app = Flask(__name__)
app.secret_key = "secret_key" # needed for flask login sessions

login_manager.init_app(app)
app.register_blueprint(auth)

@app.route("/")
def index():
    """Redirect to right page if logged in or not"""
    if current_user.is_authenticated:
        return render_template("calendar.html")
    return render_template("login.html")


# @app.route("/")
# def home():
#     """Render main page"""
#     return render_template("index.html")

@app.route("/")
def login():
    """Render login page"""
    return render_template("Login.html")

@app.route("/signup")
def signup():
    """Render Signup page"""
    return render_template("Signup.html")

@app.route("/menu")
def menu():
    """Render menu page"""
    return render_template("Menu.html")

@app.route("/calendar")
def calendar():
    """Render calendar page"""
    return render_template("Calendar.html")

@app.route("/analytics")
def analytics():
    """Render Analytics page"""
    return render_template("Analytics.html")

@app.route("/search")
def search():
    """Render Search page"""
    return render_template("Search.html")

# write new functions here
if __name__ == "__main__":
    app.run(debug=True, port=8080)
