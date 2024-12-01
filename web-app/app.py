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
from datetime import datetime
import os
import bcrypt

# Load environment variables
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DBNAME]
    users_collection = db["users"]
    bar_data_collection = db["bar"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

 
# Routes
@app.route("/")
def index():
    """Render the welcome page."""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password").encode("utf-8")

        user = users_collection.find_one({"username": username})
        if user and bcrypt.checkpw(password, user["password"]):
            session["user_id"] = str(user["_id"])
            session["username"] = username
            session.permanent = False  # Session expires when the browser is closed
            flash("Login successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password").encode("utf-8")

        # Check if username already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("signup"))

        # Insert new user into the database
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/logout")
def logout():
    """Handle user logout."""
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    """Render user dashboard."""
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))

    username = session.get("username", "User")
    return render_template("dashboard.html", username=username)


# Application entry point
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5000)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 1))),
    )
