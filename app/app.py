from bson import ObjectId
from dotenv import load_dotenv
import os, pymongo
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

load_dotenv()

mongo_uri = os.getenv("MONGO_URI") 
client = pymongo.MongoClient(mongo_uri)
db = client["wishlist"]

@app.route('/')
def home():
    # return "Connected to MongoDB Atlas!"
    return render_template('home.html')

# profile page with wishlists and resources
@app.route('/<username>')
def profile(username):
    wishlists = list(db.lists.find({"username":username}))
    return render_template('profile.html', username=username, wishlists=wishlists)

# profile page with wishlists and resources
@app.route('/<username>/add_wishlist', methods=["GET","POST"])
def add_wishlist(username):
    if request.method == "POST":
        new_wishlist = {"username":username, "items":[], "name":request.form["name"]}
        db.lists.insert_one(new_wishlist)
        return redirect(url_for("profile", username=username))
    wishlists = list(db.lists.find({"username":username}))
    return render_template('add-wishlist.html', username=username, wishlists=wishlists)

# show wishlist with items listed
@app.route('/wishlist/<id>')
def wishlist(id):
    wishlist = db.lists.find_one({"_id":ObjectId(id)})
    return render_template('wishlist.html', wishlist=wishlist)

# add item to wishlist
@app.route('/wishlist/<id>/add_item', methods=["GET", "POST"])
def add_item(id):
    if request.method == "POST":
        items = db.lists.find_one({"_id":ObjectId(id)})['items']
        new_item = {}
        new_item = { 'link':request.form['link'], 'name':request.form['name'], 'price':request.form['price']}
        items.append(new_item)
        db.lists.update_one(
                {"_id": ObjectId(id)}, {"$set": {"items": items}}
            )
        return redirect(url_for("wishlist", id=id))
    return render_template('add-item.html', id=id)

# log in
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # log in
        return redirect(url_for("profile", username=request.form["username"]))
    return render_template('login.html')

# sign up
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # placeholder output until db schema established
        new_user =  {"username":request.form["username"], "password":request.form["password"]}
        db.users.insert_one(new_user)
        return redirect(url_for("profile", username=request.form["username"]))
    return render_template('signup.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3000)
    # app.run(debug=True, port=3000)
