from flask import Flask, render_template, g, request
import csv;
import os;
import random;
import os
from dotenv import load_dotenv
from pymongo import MongoClient, server_api
import certifi


load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')

app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URI
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), server_api=server_api.ServerApi('1'))
db = client["movie_db"]
users_collection = db.users
# mongo = PyMongo(app)

def create_user(username, password):
    user = {
        "username": username,
        "password": password,  # Maybe hash this?
    }
    return user


# Runs before requests - reads csv file and puts each row into all_movies variable
@app.before_request
def read_movies():
    g.all_movies = []
    with open(os.path.join(os.path.dirname(__file__), 'input/imdb_top_1000.csv'), 'r') as file:
       csv_reader = csv.reader(file)
       for row in csv_reader:
          g.all_movies.append(row)

@app.route('/')
def index():
    user = create_user('WilliamTest','unhashedpass')
    users_collection.insert_one(user);
    # mongo.db.users.insert_one(user)
    movie_picked = False
    if not movie_picked:
        selected_movie = g.all_movies[random.randint(1,1000)]
    # for row in g.all_movies:
    #     print(row[1])
    return render_template("index.html", selectedMovie=selected_movie)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)