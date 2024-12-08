from __init__ import app, db
from flask import render_template

@app.route('/')
def home():
    books = list(db.books.find({}, {"_id": 0, "title": 1, "author": 1, "description": 1}))
    return render_template('home.html', books=books)

@app.route('/user')
def user():
    # HARDCODED! CHANGE LATER
    # WHEN LOGIN/LOGOUT FUNCTION IS ADDED
    user_id = "user1"

    user = db.users.find_one({"id": user_id}, {"_id": 0, "name": 1, "wishlist": 1, "inventory": 1})
    if not user:
        return "User not found", 404

    inventory = list(
        db.books.find(
            {"id": {"$in": user["inventory"]}},
            {"_id": 0, "title": 1, "author": 1, "description": 1}
        )
    )

    wishlist = list(
        db.books.find(
            {"id": {"$in": user["wishlist"]}},
            {"_id": 0, "title": 1, "author": 1, "description": 1}
        )
    )

    return render_template('user.html', name=user["name"], inventory=inventory, wishlist=wishlist)

@app.route('/matches')
def matches():
    return render_template('matches.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
