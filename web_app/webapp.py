from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")
EDAMAM_BASE_URL = "https://api.edamam.com/api/recipes/v2"

@app.route("/search", methods=["GET"])
def search_recipes():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    params = {
        "type": "public",
        "q": query,
        "app_id": EDAMAM_APP_ID,
        "app_key": EDAMAM_APP_KEY
    }

    try:
        response = requests.get(EDAMAM_BASE_URL, params=params)
        response.raise_for_status()

        recipes = response.json().get("hits", [])
        formatted_recipes = []

        for recipe in recipes:
            recipe_data = recipe.get("recipe", {})
            formatted_recipes.append({
                "name": recipe_data.get("label"),
                "image": recipe_data.get("image"),
                "source": recipe_data.get("source"),
                "url": recipe_data.get("url"),
                "calories": recipe_data.get("calories")
            })

        return jsonify(formatted_recipes), 200
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
