from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user
from flask_login import login_required, logout_user, current_user
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import gridfs
import pymongo
import os
import re
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

mongo_uri = os.getenv('MONGO_URI')
print(mongo_uri)
client = MongoClient(mongo_uri)

db = client.pet_base
fs = gridfs.GridFS(db)
users_collection = db.users
posts_collection = db.posts
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    """
    Represents a user in the application.

    Attributes:
        id (str): Unique identifier of the user.
        username (str): Username of the user.
    """
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username
        

@login_manager.user_loader
def load_user(user_id):
    """
    Loads a user from the database by their user ID.

    Args:
        user_id (str): The user's ID.

    Returns:
        User: A User object if the user is found, otherwise None.
    """
    user_data = users_collection.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_id=user_data["_id"], username=user_data["username"])
    return None


@app.route("/home")
@login_required
def home():
    """
    Renders the home page for the logged-in user.

    This function fetches the current user's genre statistics and song recommendations
    based on their preferences.

    Returns:
        flask.Response: The rendered 'home.html' template with:
            - genres: A list of dictionaries containing genre statistics, including:
                - "Name": The genre name.
                - "Amount": The count of songs in the genre.
                - "Percentage": The percentage of songs in the genre.
            - recommendations: A list of dictionaries containing song recommendations, including:
                - "Title": The song title.
                - "Artist": The artist's name.
                - "Genre": The genre of the song.
    """
    cur_user = current_user.username
    cur_user_collection = db[cur_user]
    genres = get_stats(cur_user_collection)
    recommendations = get_recommendations(genres)
    return render_template("home.html", genres=genres, recommendations=recommendations)


def get_stats(cur_user_collection):
    """
    Computes the genre statistics for a user's song collection.

    Args:
        cur_user_collection: The MongoDB collection corresponding to the current user,
        containing their song data.

    Returns:
        list: A list of dictionaries, where each dictionary represents a genre and contains:
            - "Name" (str): The genre name.
            - "Amount" (int): The count of songs in this genre.
            - "Percentage" (str): The percentage of songs in this genre, formatted as a string
              with two decimal places.
    """

    pipeline = [{"$group": {"_id": "$genre", "count": {"$sum": 1}}}]
    genre_counts = list(cur_user_collection.aggregate(pipeline))
    total_songs = sum(item["count"] for item in genre_counts)

    result = [
        {
            "Name": item["_id"],
            "Amount": item["count"],
            "Percentage": f"{(item['count'] / total_songs) * 100:.2f}%",
        }
        for item in genre_counts
    ]

    return result


def get_recommendations(genres):
    """
    Generates song recommendations based on the user's top genres.

    Args:
        genres (list): A list of dictionaries, where each dictionary represents
            a genre and contains:
            - "Name" (str): The genre name.
            - "Amount" (int): The count of songs in this genre.

    Returns:
            - "Title" (str): The title of the song.
            - "Artist" (str): The artist of the song.
            - "Genre" (str): The genre of the song.
    """
    sorted_genres = sorted(genres, key=lambda x: x["Amount"], reverse=True)

    if len(sorted_genres) == 0:
        return []

    top_genre = sorted_genres[0]
    second_genre = sorted_genres[1] if len(sorted_genres) > 1 else None

    total_amount = top_genre["Amount"] + (second_genre["Amount"] if second_genre else 0)
    top_genre_count = round(5 * (top_genre["Amount"] / total_amount))
    second_genre_count = 5 - top_genre_count

    recommend_collection = db["recommendations"]

    top_genre_songs = list(
        recommend_collection.aggregate(
            [
                {"$match": {"genre": top_genre["Name"]}},
                {"$sample": {"size": top_genre_count}},
            ]
        )
    )
    second_genre_songs = []
    if second_genre:
        second_genre_songs = list(
            recommend_collection.aggregate(
                [
                    {"$match": {"genre": second_genre["Name"]}},
                    {"$sample": {"size": second_genre_count}},
                ]
            )
        )

    combined_songs = top_genre_songs + second_genre_songs

    result = [
        {"Title": song["title"], "Artist": song["artist"], "Genre": song["genre"]}
        for song in combined_songs
    ]

    return result


@app.route("/addpost", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        image = request.files["image"]
        
        cur_user = current_user.username
        cur_user_collection = db[cur_user]
        
        image_id = fs.put(image.read(), filename=image.filename, content_type=image.content_type)
        
        post = {
            "user": cur_user,
            "title": title,
            "content": content,
            "image_id": image_id,
            "views": 0,
            "likes": 0,
            "liked_by": [],
            "created_at": datetime.utcnow()
        }
        inserted_post = posts_collection.insert_one(post)
        
        cur_user_collection.insert_one({"post_id": inserted_post.inserted_id})
        
        return render_template("home.html", message="Post added successfully!")
    
    return render_template("addpost.html")


@app.route("/myInfo", methods=["GET"])
@login_required
def display_my_info():
    cur_user = current_user.username
    cur_user_collection = db[cur_user]
    
    post_refs = cur_user_collection.find()
    all_posts = []

    for post_ref in post_refs:
        post = posts_collection.find_one({"_id": post_ref["post_id"]})
        image = fs.get(post["image_id"])
        image_url = f"/image/{post['image_id']}"
        
        all_posts.append({
            "post_id": str(post["_id"]),
            "title": post["title"],
            "content": post["content"],
            "image_url": image_url,
            "created_at": post.get("created_at")
        })

    return render_template("myInfo.html", posts=all_posts)


@app.route("/image/<image_id>")
def get_image(image_id):
    image = fs.get(ObjectId(image_id))
    return app.response_class(image.read(), mimetype=image.content_type)


@app.route("/posts/<post_id>", methods=["GET"])
@login_required
def display_post(post_id):
    post = posts_collection.find_one({"_id": ObjectId(post_id)})
    image = fs.get(post["image_id"])
    image_url = f"/image/{post['image_id']}"
    
    posts_collection.update_one(
        {"_id": ObjectId(post_id)}, 
        {"$inc": {"views": 1}}  # increment the views by 1
    )
    
    cur_user = current_user.username
    if cur_user in post.get('liked_by', []):
        liked = 1
    else:
        liked = 0
        
    return render_template("post.html", post=post, image_url=image_url, liked=liked)


@app.route('/like_post/<post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    cur_user = current_user.username

    post = posts_collection.find_one({"_id": ObjectId(post_id)})

    if not post:
        return jsonify({'error': 'Post not found'}), 404

    if cur_user in post.get('liked_by', []):
        # User has liked the post, so remove the like
        new_like_count = post.get('likes', 0) - 1
        posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$pull": {"liked_by": cur_user},  # removes the user from the liked_by list
                "$set": {"likes": new_like_count}
            }
        )
        action = 'removed'
    else:
        # User has not liked the post, so add the like
        new_like_count = post.get('likes', 0) + 1
        posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {
                "$addToSet": {"liked_by": cur_user},  # adds the user to the liked_by list
                "$set": {"likes": new_like_count}
            }
        )
        action = 'added'

    return jsonify({'likes': new_like_count, 'action': action})



@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Handles user registration.

    If the request method is POST, processes the registration form and creates a new user.

    Returns:
        flask.Response: The rendered 'register.html' template or a redirect to the login page.
    """
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        if password1 != password2:
            flash("Passwords do not match. Please try again.")
            return redirect(url_for("register"))

        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            flash("Username already exists. Please choose a different one.")
            return redirect(url_for("register"))
        hashed_password = generate_password_hash(password1, method="pbkdf2:sha256")
        users_collection.insert_one({"username": username, "password": hashed_password})
        db.create_collection(username)
        # flash("Registration successful! You can now log in.")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login.

    If the request method is POST, processes the login form and authenticates the user.

    Returns:
        flask.Response: The rendered 'login.html' template or a redirect to the home page.
    """
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_data = users_collection.find_one({"username": username})

        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_id=str(user_data["_id"]), username=user_data["username"])
            login_user(user)
            # flash("Login successful!")
            return redirect(url_for("home"))

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """
    Logs out the current user and redirects to the login page.

    Returns:
        flask.Response: A redirect to the login page.
    """
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
def ini():
    """
    Redirects the root URL to the login page.

    Returns:
        flask.Response: A redirect to the login page.
    """
    return redirect(url_for("home"))


def add_recommendations():
    """
    Returns:
        None

    Raises:
        FileNotFoundError: If the 'songs.txt' file is not found.
        ValueError: If the content of 'songs.txt' cannot be parsed as a valid Python list.
        pymongo.errors.PyMongoError: If there are issues with MongoDB operations.
    """
    recommend_collection = db.recommendations

    with open("songs.txt", "r", encoding="utf-8") as f:
        file_content = f.read()

    songs_dict = ast.literal_eval(file_content)
    songs = songs_dict if isinstance(songs_dict, list) else []

    if recommend_collection.count_documents({}) > 0:
        recommend_collection.delete_many({})

    recommend_collection.insert_many(songs)



if __name__ == "__main__":
    # add_recommendations()
    app.run(host="0.0.0.0", port=5002, debug=True)