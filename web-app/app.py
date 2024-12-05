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

# Load environment variables
from dotenv import load_dotenv

# Load the .env file to access environment variables
load_dotenv()

# Flask configuration
app = Flask(__name__)
# Get the secret key for session management from the environment variable
app.secret_key = ("this_is_my_random_secret_key_987654321")

# MongoDB configuration
# MongoDB connection URI and database name from environment variables
MONGO_URI = ("mongodb+srv://eh96:finalfour123@bars.ygsrg.mongodb.net/finalfour?tlsAllowInvalidCertificates=true")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)  # Create a MongoDB client
    db = client[MONGO_DBNAME]  # Access the specified database
    users_collection = db["users"]  # Access the "users" collection
    bar_data_collection = db["bar"]  # Access the "bar" collection
except Exception as e:
    # Handle errors during the connection process
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
        # Get the username and password from the form
        username = request.form.get("username")
        password = request.form.get("password").encode("utf-8")

        # Find the user in the database
        user = users_collection.find_one({"username": username})
        # Check if the user exists and the password matches
        if user and bcrypt.checkpw(password, user["password"]):
            # Set session variables for the logged-in user
            session["user_id"] = str(user["_id"])
            session["username"] = username
            session.permanent = False  # Session expires when the browser is closed
            flash("Login successful!", "success")  # Flash a success message
            return redirect(url_for("dashboard"))  # Redirect to the dashboard
        else:
            flash("Invalid username or password.", "error")  # Flash an error message

    return render_template("login.html")  # Render the login page


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handle user signup."""
    if request.method == "POST":
        # Get the username and password from the form
        username = request.form.get("username")
        password = request.form.get("password").encode("utf-8")

        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("signup"))  # Redirect back to the signup page

        # Hash the password for secure storage
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        # Insert the new user into the database
        users_collection.insert_one({"username": username, "password": hashed_password})
        flash("Account created successfully. Please log in.", "success")  # Flash success message
        return redirect(url_for("login"))  # Redirect to the login page

    return render_template("signup.html")  # Render the signup page


@app.route("/logout")
def logout():
    """Handle user logout."""
    session.clear()  # Clear the user's session
    flash("You have been logged out.", "success")  # Flash a success message
    return redirect(url_for("index"))  # Redirect to the welcome page


@app.route("/dashboard")
def dashboard():
    """Render user dashboard."""
    # Ensure the user is logged in
    if "user_id" not in session:
        flash("Please log in to access the dashboard.", "error")
        return redirect(url_for("login"))  # Redirect to the login page if not logged in

    # Get the username from the session
    username = session.get("username", "User")
    # Render the dashboard page with the username
    return render_template("dashboard.html", username=username)


@app.route("/search_saved", methods=["GET", "POST"])
def search_saved():
    """Render the search saved page."""
    if request.method == "POST":
        # Handle search functionality here (if implemented)
        search_query = request.form.get("search_query", "").strip()
        if not search_query:
            return render_template("search_saved.html", search_results=None, error="Please enter a search term.")

        # Simulated search results (REPLACE LATER with database logic)
        search_results = [
            {"name": "tempnamer", "location1": "Downtown1", "description1": "A warm and inviting bar."},
            {"name": "Skyline tempnamer", "location2": "Uptown2", "description2": "A rooftop bar with great views."}
        ]
        return render_template("search_saved.html", search_results=search_results, search_query=search_query)

    return render_template("search_saved.html", search_results=None)


@app.route("/home")
def home():
    """Render the home page."""
    return render_template("home.html")

@app.route("/findbar", methods=["GET", "POST"])
def findbar():
    if request.method == "POST":
        filter_type = request.form.get("filter_type")  # Get the selected filter
        search_query = request.form.get("search_query", "").strip()
        location_query = request.form.getlist("location_query")  # Get multiple neighborhoods
        price_query = request.form.get("price_query")  # Get price range

        query = {}

        if filter_type == "name" and search_query:
            query = {"name": {"$regex": search_query, "$options": "i"}}
        elif filter_type == "location" and location_query:
            query = {"location": {"$in": location_query}}
        elif filter_type == "price" and price_query:
            query = {"price": price_query}

        # Fetch results from the database
        search_results = list(bar_data_collection.find(query))

        return render_template(
            "findbar.html",
            search_results=search_results,
            search_query=search_query or ", ".join(location_query) or price_query,
        )

    return render_template("findbar.html", search_results=None)



# Delete bar route
@app.route('/delete/<bar_id>', methods=['POST'])
def delete_transaction(bar_id):
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    # Ensure the transaction belongs to the logged-in user
    bar_data_collection.delete_one({'_id': ObjectId(bar_id), 'username': username})  # Delete only the user's transaction
    return redirect(url_for('savedbar'))


@app.route('/savedbar', methods=['GET'])
def savedbar():
    username = session.get('username')
    # Fetch saved bars from the database
    bars = bar_data_collection.find({"username": username})
    return render_template('savedbar.html', bars=bars)


# Application entry point
if __name__ == "__main__":
    # Run the Flask app with host, port, and debug mode configurations from environment variables
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("FLASK_PORT", 5001)),
        debug=bool(int(os.getenv("FLASK_DEBUG", 1))),
    )