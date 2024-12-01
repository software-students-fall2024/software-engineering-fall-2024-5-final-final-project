from flask import (
    Flask,
    render_template,
    Response,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from pymongo import MongoClient
from datetime import datetime
import cv2
import requests
import os
import bcrypt
import base64
import numpy as np
import time

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "test_secret_key")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")
client = MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]
bar_data_collection = db["bar"]
users_collection = db["users"]

@app.route("/")
def index():
    """Render welcome page."""
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password"]):
            session["user_id"] = str(user["_id"])
            session["username"] = username
            session.permanent = False
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("signup"))

        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Clear the user's session and redirect them to the index page.
    """
    session.clear()  # Clears all session data
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # last_emotion = emotion_data_collection.find_one(
    #     {"user_id": session["user_id"]}, sort=[("timestamp", -1)]
    # )
    username = session.get("username", "User")
    return render_template(
        "dashboard.html",  username=username
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5001)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 0))),
    )
