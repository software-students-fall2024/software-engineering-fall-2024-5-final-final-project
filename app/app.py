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

# show wishlist with items listed
@app.route('/wishlist/<id>')
def wishlist(id):
    wishlist = db.lists.find_one({"_id":ObjectId(id)})
    print(wishlist)
    return render_template('wishlist.html', wishlist=wishlist)

# add item to wishlist
@app.route('/wishlist/<id>/add_item', methods=["GET", "POST"])
def add_item(id):
    if request.method == "POST":
        items = db.lists.find_one({"_id":ObjectId(id)})['items']
        print(items)
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
        # placeholder outp,ut until db schema established
        return redirect(url_for("profile", username=request.form["username"]))
    return render_template('login.html')

# sign up
@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # placeholder output until db schema established
        print(request.form["username"])
        print(request.form["password"])
    return render_template('signup.html')

if __name__ == "__main__":
    app.run(debug=True, port=3000)
    # app.run(debug=True, port=3000)
