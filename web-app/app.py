""" 
Web app frontend
"""

from flask import Flask, render_template, redirect, url_for
from flask_login import current_user, login_required, logout_user
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


# @app.route("/")
# def home():
#     """Render main page"""
#     return render_template("index.html")

@app.route("/")
def index():
    """Redirect to right page if logged in or not"""
    if current_user.is_authenticated:
        return render_template("calendar.html")
    return render_template("login.html")

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
@login_required
def analytics():
    """Render Analytics page"""
    return render_template("Analytics.html")

@app.route("/search")
@login_required
def search():
    """Render Search page"""
    return render_template("Search.html")

@app.route("/logout")
@login_required
def logout():
    "Logout route"
    logout_user()
    return redirect(url_for("index"))

# write new functions here
if __name__ == "__main__":
    app.run(debug=True, port=8080)
