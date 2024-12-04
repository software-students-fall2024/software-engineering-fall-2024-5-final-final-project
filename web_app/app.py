import os
import logging
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from pymongo import MongoClient
from dotenv import load_dotenv

import bcrypt
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "SECRET_KEY")
app.config["SESSION_PERMANENT"] = False

mongo_uri = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
client = MongoClient(mongo_uri)
db = client["whatscookin"]
users_collection = db["users"]

EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")
EDAMAM_BASE_URL = "https://api.edamam.com/api/recipes/v2"

logging.basicConfig(level=logging.INFO)


def login_required(func):
    """Decorator to ensure the user is logged in before accessing a route."""
    def wrapper(*args, **kwargs):
        if "username" not in session:
            flash("Please log in to access this page.")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route("/")
def home():
    """Render the main home page."""
    if "username" in session:
        return render_template("home.html", username=session["username"])
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in page for registered users."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password"]):
            session["username"] = username
            session.permanent = False
            return redirect(url_for("home"))
        flash("Invalid username or password. Please try again.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Registration page for new users."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"].encode("utf-8")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.")
        else:
            hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
            users_collection.insert_one(
                {"username": username, "password": hashed_password}
            )
            flash("Registration successful! Please log in.")
            return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/logout")
def logout():
    """Logs user out and clears session."""
    session.clear()
    return redirect(url_for("login"))


@app.route("/search", methods=["GET"])
def search_recipes():
    query = request.args.get("query")
    if not query:
        return render_template("recipes.html", recipes=[], query="")

    recipes_limit = 20

    params = {
        "type": "public",
        "q": query,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "from": 0,
        "to": recipes_limit,
    }

    try:
        response = requests.get(EDAMAM_BASE_URL, params=params)
        response.raise_for_status()

        recipes = response.json().get("hits", [])

        formatted_recipes = [
            {
                "name": recipe["recipe"].get("label", "N/A"),
                "image": recipe["recipe"].get("image", ""),
                "source": recipe["recipe"].get("source", "Unknown"),
                "url": recipe["recipe"].get("url", "#"),
            }
            for recipe in recipes
        ]

        return render_template(
            "recipes.html",
            recipes=formatted_recipes,
            query=query
        )
    except requests.exceptions.RequestException as e:
        return render_template(
            "recipes.html",
            recipes=[],
            query=query,
            error=str(e)
        )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
