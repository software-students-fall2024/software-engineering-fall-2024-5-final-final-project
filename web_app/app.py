import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = '7southfrogs' 

EDAMAM_APP_ID = os.getenv("EDAMAM_APP_ID")
EDAMAM_APP_KEY = os.getenv("EDAMAM_APP_KEY")
EDAMAM_BASE_URL = "https://api.edamam.com/api/recipes/v2"

@app.route("/")
def home():
    """Render the homepage."""
    user = session.get("user") 
    return render_template("home.html", user=user)



@app.route("/search", methods=["GET"])
def search_recipes():
    query = request.args.get("query")
    if not query:
        return jsonify({"error": "Query parameter is required"}), 400

    page = request.args.get("page", 1, type=int)
    recipes_per_page = 10

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
        if not recipes:
            return jsonify({"error": "No recipes found"}), 404

        # Extract recipes for the current page
        total_recipes = len(recipes)
        start_index = (page - 1) * recipes_per_page
        end_index = start_index + recipes_per_page
        paginated_recipes = recipes[start_index:end_index]

        # Format recipes
        formatted_recipes = []
        for recipe in paginated_recipes:
            recipe_data = recipe.get("recipe", {})
            formatted_recipes.append({
                "name": recipe_data.get("label", "N/A"),
                "image": recipe_data.get("image", ""),
                "source": recipe_data.get("source", "N/A"),
                "url": recipe_data.get("url", "#")
            })

        # Determine if there's a next page
        has_next = end_index < total_recipes

        # Render template with paginated recipes
        return render_template(
            "recipes.html",
            recipes=formatted_recipes,
            page=page,
            has_next=has_next,
            query=query
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Render the login page and handle login logic."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        # Placeholder for actual login logic (e.g., checking with MongoDB)
        session["user"] = username  # Save the username in session
        return redirect(url_for("home"))  # Redirect to homepage on successful login
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Log out the user by clearing the session."""
    session.pop("user", None)  # Remove user from session
    return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():
    """Render the register page and handle user registration."""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        # Handle registration logic here (e.g., save user to the database)
        return redirect(url_for("login"))  # Redirect to login page on successful registration
    return render_template("register.html")

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
