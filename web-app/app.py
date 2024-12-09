from flask import Flask, render_template, g, request, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import csv
import os
import random
from dotenv import load_dotenv
from pymongo import MongoClient, server_api
from bson.objectid import ObjectId
import certifi, datetime


load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
db_name = os.getenv('MONGO_DBNAME')

class User(UserMixin):
    def __init__(self, username, id):
        self.username = username
        self.id = id

    def get_id(self):
        return self.id

def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config["MONGO_URI"] = MONGO_URI
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), server_api=server_api.ServerApi('1'))
    db = client["movie_db"]
    users_collection = db.users
    ratings_collection = db.ratings
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader  
    def load_user(id):
        user_data = db.users.find_one({"_id": ObjectId(id)})
        if user_data:
            return User(username=user_data['username'], id=str(user_data['_id']))
        return None

    def create_user(username, password):
        user = {
            "username": username,
            "password": password,  # Maybe hash this?
            "daily_movie":{
                "movie_id": random.randint(1,1000),
                "recommended_date": datetime.datetime.now()
            },
            "watched_movies": []
        }
        return user

    def random_movie_id(watched_ids):
        id = 0
        while True:
            id = random.randint(1,1000)
            if id not in watched_ids:
                break
        return id

    @app.before_request
    def read_movies():
        g.all_movies = []
        try:
            with open(os.path.join(os.path.dirname(__file__), 'input/imdb_top_1000.csv'), 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    g.all_movies.append(row)
        except FileNotFoundError:
            g.all_movies = []
            print("Error: CSV file not found.")
        except Exception as e:
            print(f"Error reading CSV file: {e}")

    @app.route('/')
    def index():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        # user = create_user('WilliamTest2','unhashedpass')
        # users_collection.insert_one(user);
        # mongo.db.users.insert_one(user)

        # TODO: This will have to change to find the user that is logged in, hardcoded for now to test
        
        selected_user = users_collection.find_one({"_id":ObjectId(current_user.id)})

        # print("User's date: " + selected_user["daily_movie"]["recommended_date"].strftime("%Y %m %d"))
        # print("Computer's date: " + datetime.datetime.now().strftime("%Y %m %d"))
        # print("Equal?: "+ str(selected_user["daily_movie"]["recommended_date"] == datetime.datetime.now()))

        # Checks if movie has been assigned for the day if last recommended movie date is same as today
         # Ensure the daily_movie key exists
        if "daily_movie" not in selected_user:
            # Initialize daily_movie if missing
            selected_user["daily_movie"] = {
                "movie_id": random.randint(1, 1000),
                "recommended_date": datetime.datetime.now()
            }
            users_collection.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$set": {"daily_movie": selected_user["daily_movie"]}}
            )
        
        user_movie_id = selected_user["daily_movie"]["movie_id"]
        user_recommended_date = selected_user["daily_movie"]["recommended_date"]
        
        is_already_assigned = user_recommended_date.strftime("%Y %m %d") == datetime.datetime.now().strftime("%Y %m %d")

        # # For testing: to forcefully update movie even if date hasn't changed
        # is_already_assigned = False

        # if movie hasn't been assigned for the day, set a new movie that user hasn't seen before
        if not is_already_assigned:
            new_movie_id = random_movie_id(selected_user["watched_movies"])
            users_collection.update_one(
                {"_id":ObjectId(current_user.id)},    # TODO: replace username with actual user logged in
                { 
                    "$set": {
                        "daily_movie.movie_id": new_movie_id,
                        "daily_movie.recommended_date": datetime.datetime.now()
                    }
                }
            )
            selected_movie = g.all_movies[new_movie_id] # uses newly generated movie id
            movie_id = new_movie_id

        # if move has been assigned
        else:
            selected_movie = g.all_movies[user_movie_id] # uses existing movie id found in user doc in db
            movie_id = user_movie_id
        return render_template("index.html", selectedMovie=selected_movie, movieId=movie_id)
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        error = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            if not username or not password or not confirm_password:
                error = 'Username and password are required!'
            elif db.users.find_one({"username": username}):
                error = 'Username already exists. Choose another one.'
            elif password != confirm_password:
                error = 'Passwords do not match!'
            else:
                users_collection.insert_one(create_user(username, password));
                return redirect(url_for('login'))
        return render_template('register.html', error=error)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        error = None
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user_data = db.users.find_one({"username": username})
            if user_data and user_data["password"] == password:
                user = User(username=user_data['username'],id=str(user_data['_id']))
                login_user(user)
                return redirect(url_for('profile', user=username))
            else:
                error = "Invalid username or password."
        return render_template('login.html', error=error)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/profile/<user>')
    @login_required
    def profile(user):
        user = users_collection.find_one({"username": "WilliamTest2"})
        
        # Get the watched movies for the user
        watched_movies_ids = [
            rating["movie_id"] for rating in ratings_collection.find({"user": user["_id"]})
        ]
        
        # Fetch movie details for the watched movies
        watched_movies = [g.all_movies[movie_id] for movie_id in watched_movies_ids]

        # Render the profile template with user and watched movies data
        return render_template(
            "profile.html",
            user=user["username"],
            watchedMovies=watched_movies
        )

    @app.route('/setwatched', methods=["POST"])
    def setWatched():
        user = users_collection.find_one({"_id":ObjectId(current_user.id)})

        # Check if the checkbox is checked (it will be 'true' if checked, and 'false' if unchecked)
        has_watched = request.form.get('hasWatched') == 'true'
        movie_id = int(request.form['movieId'])

        print(has_watched)

        if has_watched:
            ratings_collection.insert_one(
                {
                    "user": user["_id"],
                    "movie_id": movie_id,
                    "date_watched": datetime.datetime.now()
                }
            )

            users_collection.update_one(
                {"_id": user["_id"]},
                {"$push": {"watched_movies": movie_id}}
            )
        else:
            ratings_collection.delete_one({
                "user": user["_id"],
                "movie_id": movie_id
            })

            users_collection.update_one(
                {"_id": user["_id"]},
                {"$pop": {"watched_movies": 1}}
            )

        # Return to the homepage or wherever you need to redirect after processing
        return redirect(url_for("index"))

    @app.route('/watchlist')
    def watchlist():
        selected_user = users_collection.find_one({"_id":ObjectId(current_user.id)})
        watched_movies = []

        # Fetch watched movies based on the user's watched_movies list
        for movie_id in selected_user.get("watched_movies", []):
            watched_movie = g.all_movies[movie_id]
            watched_movies.append(watched_movie)

        return render_template("watchlist.html", watchedMovies=watched_movies)
    return app
if __name__ == '__main__':
    FLASK_PORT = os.getenv("FLASK_PORT", "3000")
    app = create_app()
    app.run(host="0.0.0.0", port=3000)

    

