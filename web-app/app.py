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
import os
import bcrypt
from dotenv import load_dotenv
from dream_analysis import analyze_dream
import nltk
nltk.download('punkt')
nltk.download('stopwords')  # Download stopwords resource

# Set a custom nltk_data directory (e.g., inside your project folder)
nltk_data_path = os.path.expanduser('~/nltk_data')
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)

# Add the path to NLTK's search paths
nltk.data.path.append(nltk_data_path)

# Ensure stopwords resource is available
try:
    nltk.download("stopwords", download_dir=nltk_data_path)
except Exception as e:
    print(f"Error downloading NLTK resources: {e}")


# pylint: disable=all

# Load environment variables
load_dotenv()

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "test_secret_key")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")
client = MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]
dream_data_collection = db["dream_data"]
users_collection = db["users"]

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

@app.route("/")
def index():
    """Render welcome page."""
    return render_template("index.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    username = session.get("username", "User")
    dream_interpretation = None

    if request.method == "POST":
        # Get the dream description from the form
        dream_description = request.form.get("dream_description", "")
        
        # Analyze the dream using the dream_analysis module
        dream_interpretation = analyze_dream(dream_description)
        
        # Save the dream and interpretation to the database
        dream_data_collection.insert_one({
            "user_id": session["user_id"],
            "dream_description": dream_description,
            "dream_interpretation": dream_interpretation,
            "timestamp": datetime.utcnow()
        })

    # Fetch the last dream interpretation for the user
    last_dream = dream_data_collection.find_one(
        {"user_id": session["user_id"]}, sort=[("timestamp", -1)]
    )

    return render_template(
        "dashboard.html", 
        username=username, 
        last_dream=last_dream, 
        dream_interpretation=dream_interpretation
    )

@app.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Clear the user's session and redirect them to the index page.
    """
    session.clear()  
    return redirect(url_for("index"))

@app.route("/journal", methods=["GET"])
def journal():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Fetch all dreams for the logged-in user
    journal_entries = list(dream_data_collection.find({"user_id": session["user_id"]}).sort("timestamp", -1))
    return render_template("journal.html", journal_entries=journal_entries)


@app.route("/entry", methods=["GET", "POST"])
@app.route("/entry/<entry_id>", methods=["GET", "POST"])
def entry(entry_id=None):
    if "user_id" not in session:
        return redirect(url_for("login"))

    entry = None
    if entry_id:
        entry = dream_data_collection.find_one({"_id": ObjectId(entry_id)})

    if request.method == "POST":
        dream_description = request.form["dream_description"]
        analysis = analyze_dream(dream_description)

        if entry:
            # Update existing entry
            dream_data_collection.update_one(
                {"_id": ObjectId(entry_id)},
                {"$set": {"dream_description": dream_description, "analysis": analysis}}
            )
        else:
            # Add a new entry
            dream_data_collection.insert_one({
                "user_id": session["user_id"],
                "dream_description": dream_description,
                "analysis": analysis,
                "timestamp": datetime.utcnow()
            })

        return redirect(url_for("journal"))

    return render_template("entry.html", entry=entry)

@app.route("/delete/<entry_id>", methods=["POST"])
def delete_entry(entry_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    dream_data_collection.delete_one({"_id": ObjectId(entry_id), "user_id": session["user_id"]})
    return redirect(url_for("journal"))




if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5001)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 0))),
    )
    
    