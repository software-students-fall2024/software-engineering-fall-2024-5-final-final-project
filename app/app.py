"""
Flask API for managing wishlists.
Handles routes for wishlist creation, retrieval, and updates.
"""
import os
import pymongo
from bson import ObjectId
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = pymongo.MongoClient(mongo_uri)
db = client["wishlist"]


@app.route("/")
def home():
    """
    Home route that renders the homepage.
    """
    return render_template("home.html")


@app.route("/<username>")
def profile(username):
    """
    Profile page for a user displaying their wishlists.
    
    Args:
        username (str): Username of the profile owner.
    
    Returns:
        Rendered HTML template for the profile page.
    """
    user_wishlists = list(db.lists.find({"username": username}))
    return render_template("profile.html", username=username, wishlists=user_wishlists)


@app.route("/<username>/add_wishlist", methods=["GET", "POST"])
def add_wishlist(username):
    """
    Route to add a new wishlist for a user.
    
    Args:
        username (str): Username of the profile owner.
    
    Returns:
        Redirects to the profile page after adding a wishlist or renders the add wishlist page.
    """
    if request.method == "POST":
        new_wishlist = {"username": username, "items": [], "name": request.form["name"]}
        db.lists.insert_one(new_wishlist)
        return redirect(url_for("profile", username=username))
    user_wishlists = list(db.lists.find({"username": username}))
    return render_template("add-wishlist.html", username=username, wishlists=user_wishlists)


@app.route("/wishlist/<wishlist_id>")
def wishlist_view(wishlist_id):
    """
    Route to display a specific wishlist with its items.
    
    Args:
        wishlist_id (str): ID of the wishlist.
    
    Returns:
        Rendered HTML template for the wishlist page.
    """
    user_wishlist = db.lists.find_one({"_id": ObjectId(wishlist_id)})
    return render_template("wishlist.html", wishlist=user_wishlist)


@app.route("/wishlist/<wishlist_id>/add_item", methods=["GET", "POST"])
def add_item(wishlist_id):
    """
    Route to add an item to a specific wishlist.
    
    Args:
        wishlist_id (str): ID of the wishlist.
    
    Returns:
        Redirects to the wishlist page after adding an item or renders the add item page.
    """
    if request.method == "POST":
        wishlist_items = db.lists.find_one({"_id": ObjectId(wishlist_id)})["items"]
        new_item = {
            "link": request.form["link"],
            "name": request.form["name"],
            "price": request.form["price"],
        }
        wishlist_items.append(new_item)
        db.lists.update_one({"_id": ObjectId(wishlist_id)}, {"$set": {"items": wishlist_items}})
        return redirect(url_for("wishlist_view", wishlist_id=wishlist_id))
    return render_template("add-item.html", id=wishlist_id)


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Route for user login.
    
    Returns:
        Redirects to the profile page after successful login or renders the login page.
    """
    if request.method == "POST":
        return redirect(url_for("profile", username=request.form["username"]))
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """
    Route for user signup.
    
    Returns:
        Redirects to the profile page after successful signup or renders the signup page.
    """
    if request.method == "POST":
        new_user = {
            "username": request.form["username"],
            "password": request.form["password"],
        }
        db.users.insert_one(new_user)
        return redirect(url_for("profile", username=request.form["username"]))
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
