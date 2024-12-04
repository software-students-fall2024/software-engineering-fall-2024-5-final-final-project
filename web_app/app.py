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
    username = session.get("username")
    return render_template("home.html", username=username)


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


HEALTH_LABELS = [
    {"web_label": "Alcohol-Cocktail", "api_param": "alcohol-cocktail"},
    {"web_label": "Alcohol-Free", "api_param": "alcohol-free"},
    {"web_label": "Celery-Free", "api_param": "celery-free"},
    {"web_label": "Crustacean-Free", "api_param": "crustacean-free"},
    {"web_label": "Dairy-Free", "api_param": "dairy-free"},
    {"web_label": "DASH", "api_param": "DASH"},
    {"web_label": "Egg-Free", "api_param": "egg-free"},
    {"web_label": "Fish-Free", "api_param": "fish-free"},
    {"web_label": "FODMAP-Free", "api_param": "fodmap-free"},
    {"web_label": "Gluten-Free", "api_param": "gluten-free"},
    {"web_label": "Immuno-Supportive", "api_param": "immuno-supportive"},
    {"web_label": "Keto-Friendly", "api_param": "keto-friendly"},
    {"web_label": "Kidney-Friendly", "api_param": "kidney-friendly"},
    {"web_label": "Kosher", "api_param": "kosher"},
    {"web_label": "Low Potassium", "api_param": "low-potassium"},
    {"web_label": "Low Sugar", "api_param": "low-sugar"},
    {"web_label": "Lupine-Free", "api_param": "lupine-free"},
    {"web_label": "Mediterranean", "api_param": "Mediterranean"},
    {"web_label": "Mollusk-Free", "api_param": "mollusk-free"},
    {"web_label": "Mustard-Free", "api_param": "mustard-free"},
    {"web_label": "No oil added", "api_param": "No-oil-added"},
    {"web_label": "Paleo", "api_param": "paleo"},
    {"web_label": "Peanut-Free", "api_param": "peanut-free"},
    {"web_label": "Pescatarian", "api_param": "pecatarian"},
    {"web_label": "Pork-Free", "api_param": "pork-free"},
    {"web_label": "Red-Meat-Free", "api_param": "red-meat-free"},
    {"web_label": "Sesame-Free", "api_param": "sesame-free"},
    {"web_label": "Shellfish-Free", "api_param": "shellfish-free"},
    {"web_label": "Soy-Free", "api_param": "soy-free"},
    {"web_label": "Sugar-Conscious", "api_param": "sugar-conscious"},
    {"web_label": "Sulfite-Free", "api_param": "sulfite-free"},
    {"web_label": "Tree-Nut-Free", "api_param": "tree-nut-free"},
    {"web_label": "Vegan", "api_param": "vegan"},
    {"web_label": "Vegetarian", "api_param": "vegetarian"},
    {"web_label": "Wheat-Free", "api_param": "wheat-free"}
]

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Render and update the user's dietary restrictions."""
    username = session["username"]

    if request.method == "POST":
        # Save dietary restrictions to the database
        dietary_restrictions = request.form.getlist("restrictions")
        users_collection.update_one(
            {"username": username},
            {"$set": {"dietary_restrictions": dietary_restrictions}}
        )
        flash("Dietary restrictions updated successfully.")
        return redirect(url_for("profile"))

    # Retrieve current dietary restrictions from the database
    user = users_collection.find_one({"username": username})
    dietary_restrictions = user.get("dietary_restrictions", []) if user else []

    return render_template(
        "profile.html",
        dietary_restrictions=dietary_restrictions,
        health_labels=HEALTH_LABELS
    )


@app.route("/search", methods=["GET"])
@login_required
def search_recipes():
    query = request.args.get("query")
    if not query:
        return render_template("recipes.html", recipes=[], query="", page=1, total_pages=1, has_next=False)

    page = request.args.get("page", 1, type=int)
    recipes_per_page = 10

    from_index = (page - 1) * recipes_per_page
    to_index = from_index + recipes_per_page

    # Retrieve dietary restrictions from the database
    username = session["username"]
    user = users_collection.find_one({"username": username})
    dietary_restrictions = user.get("dietary_restrictions", []) if user else []

    params = {
        "type": "public",
        "q": query,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "from": from_index,
        "to": to_index,
    }

    # Include dietary restrictions in the API call
    for restriction in dietary_restrictions:
        params.setdefault("health", []).append(restriction)

    try:
        response = requests.get(EDAMAM_BASE_URL, params=params)
        response.raise_for_status()

        recipes = response.json().get("hits", [])
        total_recipes = response.json().get("count", 0)

        total_pages = min((total_recipes + recipes_per_page - 1) // recipes_per_page, 10)

        formatted_recipes = [
            {
                "name": recipe["recipe"].get("label", "N/A"),
                "image": recipe["recipe"].get("image", ""),
                "source": recipe["recipe"].get("source", "Unknown"),
                "url": recipe["recipe"].get("url", "#"),
            }
            for recipe in recipes
        ]

        has_next = page < total_pages

        return render_template(
            "recipes.html",
            recipes=formatted_recipes,
            query=query,
            page=page,
            total_pages=total_pages,
            has_next=has_next,
        )
    except requests.exceptions.RequestException as e:
        return render_template("recipes.html", recipes=[], query=query, page=1, total_pages=1, has_next=False, error=str(e))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
