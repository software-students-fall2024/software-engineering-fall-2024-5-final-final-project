""" 
Web app frontend
"""

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import current_user, login_required, logout_user
import os
from pymongo.mongo_client import MongoClient
from user.auth import auth, login_manager

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/theonepiece")
client = MongoClient(mongo_uri)
db = client.get_default_database()

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/theonepiece")
client = MongoClient(mongo_uri)
db = client.get_default_database()

app = Flask(__name__)
app.secret_key = "secret_key"  # needed for flask login sessions

login_manager.init_app(app)
app.register_blueprint(auth)


# @app.route("/")
# def home():
#     """Render main page"""
#     return render_template("index.html")


@app.route("/")
def index():
    """Redirect to right page if logged in or not"""
    if current_user.is_authenticated:
        return render_template("calendar.html")
    return render_template("Login.html")


@app.route("/signup")
def signup():
    """Render Signup page"""
    return render_template("Signup.html")


@login_required
@app.route("/menu")
def menu():
    """Render menu page"""
    return render_template("Menu.html")


@login_required
@app.route("/calendar")
def calendar():
    """Render calendar page"""
    return render_template("Calendar.html")


@app.route("/analytics")
@login_required
def analytics():
    """Render Analytics page"""
    return render_template("Analytics.html")


@app.route("/search")
@login_required
def search():
    """Render Search page"""
    return render_template("Search.html")



@app.route("/user-info")
@login_required
def getUserInfo():
    # retrieve user info and return with template
    user_info = {
        "username": current_user.username,
        "password": current_user.password,
        "firstname": current_user.firstname,
        "lastname": current_user.lastname,
    }

    return render_template("edit-user-info.html", user_info=user_info)


@app.route("/update-info")
@login_required
def getUpdatePage():
    user_info = {
        "username": current_user.username,
        "firstname": current_user.firstname,
        "lastname": current_user.lastname,
    }

    return render_template("edit-user-info.html", user_info=user_info)


@app.route("/user-info", methods=["POST"])
@login_required
def updateUserInfo():
    # getting firstname and last name from the HTML form
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]

    # update the user's first name and last name in the mongodb
    db.users.update_one(
        {"username": current_user.username},
        {"$set": {"firstname": firstname, "lastname": lastname}},
    )

    # update the current_user object on flask app
    current_user.firstname = firstname
    current_user.lastname = lastname

    return redirect(url_for("getUserInfo"))


# write new functions here
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
