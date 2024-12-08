"""
This module contains the web application for the journal app using Flask and MongoDB.
"""

import os
import calendar
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import requests

# Load environment variables
load_dotenv()

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "test_secret_key")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client[MONGO_DBNAME]
users_collection = db["users"]
journal_collection = db["journals"]

# ML Client configuration
ML_CLIENT_URL = os.getenv("ML_CLIENT_URL", "http://ml-client:5002/analyze")


@app.route("/")
def index():
    """
    Redirect to the login page.
    """
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    User registration page.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose another.", "error")
            return redirect(url_for("register"))

        try:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            users_collection.insert_one({"username": username, "password": hashed_password})
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
            return redirect(url_for("register"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    User login page.
    """
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = users_collection.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = username
            return redirect(url_for("calendar_"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    Logout the current user.
    """
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("login"))


@app.route("/calendar", methods=["GET"])
def calendar_():
    if "user_id" not in session:
        return redirect(url_for("login"))

    now = datetime.utcnow()
    year, month = now.year, now.month
    month_days = calendar.monthcalendar(year, month)

    user_id = session["user_id"]
    journal_entries = {
        entry["day"]: {
            "id": entry["_id"],
            "analysis": entry.get("analysis", {"top_emotion": {"label": "default"}})
        }
        for entry in journal_collection.find({"user_id": user_id, "month": month, "year": year})
    }

    return render_template(
        "calendar.html",
        year=year,
        month=month,
        month_days=month_days,
        journal_entries=journal_entries,
    )



def perform_analysis(content):
    """
    Perform ML analysis on the provided content.
    Sends the content to the ML client and retrieves the analysis results.
    """
    try:
        response = requests.post(ML_CLIENT_URL, json={"text": content})
        if response.status_code == 200:
            return response.json()  # Return the analysis result
        else:
            flash("Error in ML analysis.", "error")
            return {}
    except Exception as e:
        flash(f"Failed to analyze journal entry: {e}", "error")
        return {}


@app.route("/journal/<int:year>/<int:month>/<int:day>", methods=["GET", "POST"])
def journal(year, month, day):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    date = f"{year}-{month:02d}-{day:02d}"
    entry = journal_collection.find_one({"user_id": user_id, "date": date})

    if request.method == "POST":
        content = request.form.get("content")
        if not content:
            flash("Content cannot be empty.", "error")
            return redirect(url_for("journal", year=year, month=month, day=day))

        # Analyze the content
        analysis = perform_analysis(content)

        if entry:
            # Update existing entry
            journal_collection.update_one(
                {"_id": entry["_id"]},
                {"$set": {"content": content, "analysis": analysis}}
            )
            flash("Journal entry updated.", "success")
        else:
            # Create a new entry
            journal_collection.insert_one({
                "user_id": user_id,
                "date": date,
                "content": content,
                "analysis": analysis,
                "year": year,
                "month": month,
                "day": day,
            })
            flash("Journal entry added.", "success")
        return redirect(url_for("journal", year=year, month=month, day=day))

    return render_template("journal.html", date=date, entry=entry)



@app.route("/delete/<entry_id>", methods=["POST"])
def delete_entry(entry_id):
    """
    Delete a journal entry.
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    journal_collection.delete_one({"_id": ObjectId(entry_id)})
    flash("Journal entry deleted.", "success")
    return redirect(url_for("calendar_"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5001)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 1))),
    )

