from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os
import bcrypt
import pandas as pd
import json
 
from dotenv import load_dotenv

load_dotenv()  # load .env file
app = Flask(__name__)
app.secret_key = "this_is_my_random_secret_key_987654321"
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://eh96:finalfour123@bars.ygsrg.mongodb.net/finalfour?tlsAllowInvalidCertificates=true")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "finalfour")

# Connect to MongoDB
client = MongoClient(MONGO_URI)  # create MongoDB client
db = client[MONGO_DBNAME]  # access database
users_collection = db["users"]  # collection of users
bars_collection = db["bars"]  # collection of bars

# --------ACCOUNT PAGE--------
@app.route("/account")
def account():
    """
    Render the account page where the user can log in or sign up.
    """
    return render_template("account.html")


# --------LOGIN PAGE--------
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login.
    - GET: Render the login page.
    - POST: Authenticate the user.
    """
    if request.method == "POST":
        username = request.form["username"].strip()  # Get the username
        raw_password = request.form["password"].strip()  # Get the password

        # Convert password to bytes
        password_bytes = raw_password.encode("utf-8")

        # Find the user in the database
        user = users_collection.find_one({"username": username})

        if user and "password" in user:
            # Verify the password using bcrypt
            stored_hashed_password = user["password"]
            if bcrypt.checkpw(password_bytes, stored_hashed_password):
                # Login successful
                session["user_id"] = str(user["_id"])
                session["username"] = username
                session.permanent = False
                return redirect(url_for("index"))
            else:
                # Invalid password
                flash("Invalid username or password.", "error")
                return redirect(url_for("login"))
        else:
            # User not found
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

    # Render the login template
    return render_template("login.html")


# --------SIGNUP PAGE--------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Handle user registration.
    - GET: Render the signup page.
    - POST: Register a new user.
    """
    if request.method == "POST":
        username = request.form["username"].strip()  # Get the username
        raw_password = request.form["password"].strip()  # Get the password

        # Convert password to bytes
        password_bytes = raw_password.encode("utf-8")

        # Check if username already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("signup"))

        # Hash the password and store in the database
        hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    # Render the signup template
    return render_template("signup.html")


# --------HOME PAGE--------
@app.route("/")
def index():
    """
    Render the home page, showing the user's saved bars.
    Redirects to the account page if the user is not logged in.
    """
    if "user_id" not in session:
        return redirect(url_for("account"))

    # Fetch all bars saved by the current user
    user_id = session.get("user_id")
    bars = bars_collection.find({"user_id": user_id})

    return render_template("index.html", bars=bars, username=session.get("username"))


# --------ADD PAGE--------
@app.route("/add", methods=["GET", "POST"])
def add():
    """
    Handle adding a new bar.
    - GET: Render the add page.
    - POST: Save the new bar to the database.
    """
    if request.method == "POST":
        # Gather form data
        name = request.form.get("name")
        type = request.form.get("type")
        occasion = request.form.get("occasion")
        area = request.form.get("area")
        reservation = request.form.get("reservation")
        cost = request.form.get("cost")
        status = request.form.get("status")

        # Create a new bar entry
        new_bar = {
            "user_id": session.get("user_id"),
            "name": name,
            "type": type,
            "occasion": occasion,
            "area": area,
            "reservation": reservation,
            "cost": cost,
            "status": status,
        }
        bars_collection.insert_one(new_bar)  # Insert into database
        return redirect(url_for("index"))

    return render_template("add.html")


# --------EDIT PAGE--------
@app.route("/edit/<bar_id>", methods=["GET", "POST"])
def edit(bar_id):
    """
    Handle editing an existing bar.
    - GET: Render the edit page.
    - POST: Update the bar details in the database.
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Fetch the bar details to be edited
    bar = bars_collection.find_one(
        {"_id": ObjectId(bar_id), "user_id": session.get("user_id")}
    )
    if not bar:
        return redirect(url_for("index"))

    if request.method == "POST":
        # Update the bar details
        name = request.form.get("name")
        type = request.form.get("type")
        occasion = request.form.get("occasion")
        area = request.form.get("area")
        reservation = request.form.get("reservation")
        cost = request.form.get("cost")
        status = request.form.get("status")

        # Update the database
        bars_collection.update_one(
            {"_id": ObjectId(bar_id), "user_id": session.get("user_id")},
            {
                "$set": {
                    "name": name,
                    "type": type,
                    "occasion": occasion,
                    "area": area,
                    "reservation": reservation,
                    "cost": cost,
                    "status": status,
                }
            },
        )
        return redirect(url_for("index"))

    return render_template("edit.html", bar=bar)


# --------DELETE PAGE--------
@app.route("/delete/<bar_id>", methods=["GET", "POST"])
def delete(bar_id):
    """
    Handle deleting a bar.
    - GET: Confirm deletion.
    - POST: Delete the bar from the database.
    """
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Fetch the bar to be deleted
    bar = bars_collection.find_one(
        {"_id": ObjectId(bar_id), "user_id": session.get("user_id")}
    )
    if not bar:
        return redirect(url_for("index"))

    # Delete the bar
    if request.method == "POST":
        bars_collection.delete_one(
            {"_id": ObjectId(bar_id), "user_id": session.get("user_id")}
        )
        return redirect(url_for("index"))

    return render_template("delete.html", bar=bar)
 
# --------SEARCH PAGE--------
@app.route("/search", methods=["GET", "POST"])
def search():
    if "user_id" not in session:
        return redirect(url_for("login"))  # direct to login.html

    # query variables
    query = {"user_id": session.get("user_id")}  # user-specific
    category = request.form.get("category")
    search_value = request.form.get(category)

    # query based on chosen category (partial vs exact matching)
    if category:
        if category == "Name":
            if isinstance(search_value, str):
                query[category] = {"$regex": search_value, "$options": "i"}
        else:
            query[category] = search_value  # exact matching (drown-drop cats)

    bars = list(bars_collection.find(query))  # search by category

    return render_template("search.html", bars=bars, category=category)  # link to html


# --------SORT PAGE--------
@app.route("/sort", methods=["GET", "POST"])
def sort():
    if "user_id" not in session:
        return redirect(url_for("login"))  # direct to login.html

    if request.method == "POST":
        # get data
        category = request.form.get("category")
        order = request.form.get("order")

        # set sort order: 1 = ascending, -1 = descending
        if order == "asc":
            sort_order = 1
        else:
            sort_order = -1

        # query sort bars
        query = {"user_id": session.get("user_id")}
        bars = list(bars_collection.find(query).sort(category, sort_order))

        # noramlize status field
        for bar in bars:
            if bar.get("status") == "Not Visited":
                bar["status"] = "No"
            elif bar.get("status") == "Visited":
                bar["status"] = "Yes"

        return render_template("sort.html", bars=bars)

    return render_template("sort.html", bars=[])  # link to sort.html


# --------RECOMMENDATIONS PAGE--------
from web_app.recommender.recommender import load_bars, preprocess_bars, compute_sim_matrix, recommend_bars


@app.route("/recs", methods=["GET", "POST"])
def recommend():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    # Get user's bars from MongoDB
    user_bars = list(bars_collection.find({"user_id": user_id}))
    user_bar_names = [bar["name"] for bar in user_bars]

    # Load and preprocess bar data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    bars_json_path = os.path.join(current_dir, "recommender", "bars.json")

    if not os.path.exists(bars_json_path):
        raise FileNotFoundError(f"bars.json file not found at {bars_json_path}")

    # Load JSON file and create DataFrame
    with open(bars_json_path, "r") as file:
        bars_data = json.load(file)

    # Normalize JSON structure into a DataFrame
    bars_df = pd.json_normalize(bars_data)

    # Ensure proper columns exist
    required_columns = [
        "Name",
        "Type",
        "Occasion",
        "Area",
        "Reservation",
        "Cost",
        "Rating",
    ]
    if not all(col in bars_df.columns for col in required_columns):
        raise ValueError(
            f"The JSON data is missing required columns: {required_columns}"
        )

    # Select only the required columns
    bars_df = bars_df[required_columns]

    # Remove user's existing bars from recommendations
    bars_df = bars_df[~bars_df["Name"].isin(user_bar_names)]

    # Preprocess and compute recommendations
    bars_df = preprocess_bars(bars_df)
    cosine_sim = compute_sim_matrix(bars_df)
    recommendations = recommend_bars(user_bar_names, bars_df, cosine_sim)
    while len(recommendations) < 5 and len(bars_df) > len(recommendations):
        for _, bar in bars_df.iterrows():
            if bar["Name"] not in [rec["name"] for rec in recommendations]:
                recommendations.append(
                    {
                        "name": bar["Name"],
                        "type": bar["Type"],
                        "occasion": bar["Occasion"],
                        "area": bar["Area"],
                        "reservation": bar["Reservation"],
                        "cost": bar["Cost"],
                    }
                )
                if len(recommendations) == 5:
                    break

    if request.method == "POST":
        bar_name = request.form.get("bar_name")
        if bar_name:
            bar_to_add = next(
                (bar for bar in recommendations if bar["name"] == bar_name), None
            )
            if bar_to_add:
                # Add bar to the user's database
                new_bar = {
                    "user_id": user_id,
                    "name": bar_to_add["name"],
                    "type": bar_to_add["type"],
                    "occasion": bar_to_add["occasion"],
                    "area": bar_to_add["area"],
                    "reservation": bar_to_add["reservation"],
                    "cost": bar_to_add["cost"],
                    "status": "Not Visited",
                }
                bars_collection.insert_one(new_bar)
                flash(f"Added {bar_name} to your list!", "success")
                return redirect(url_for("recommend"))

    return render_template("recommend.html", bars=recommendations)



# --------LOGOUT PAGE--------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("account"))  # link to account.html


# MAIN METHOD
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 1))),
    )