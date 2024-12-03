import os
from flask import Flask, request, jsonify, render_template
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")
EDAMAM_BASE_URL = "https://api.edamam.com/api/recipes/v2"

@app.route("/")
def home():
    """Render the homepage."""
    return render_template("home.html")


@app.route("/search", methods=["GET"])
def search_recipes():
    query = request.args.get("query")
    if not query:
        return render_template("recipes.html", recipes=[], query="", page=1, total_pages=1, has_next=False)

    page = request.args.get("page", 1, type=int)
    recipes_per_page = 10

    from_index = (page - 1) * recipes_per_page
    to_index = from_index + recipes_per_page

    params = {
        "type": "public",
        "q": query,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY,
        "from": from_index,
        "to": to_index,
    }

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
