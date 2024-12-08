from flask import Flask, render_template, g, request
import csv;
import os;
import random;
import os
from dotenv import load_dotenv
from pymongo import MongoClient, server_api
import certifi, datetime


load_dotenv()

MONGO_URI = os.getenv('MONGO_URI')
db_name = os.getenv('MONGO_DBNAME')

app = Flask(__name__)

app.config["MONGO_URI"] = MONGO_URI
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), server_api=server_api.ServerApi('1'))
db = client[db_name]
users_collection = db.users
# mongo = PyMongo(app)

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
    id = 0;
    while True:
        id = random.randint(1,1000)
        if id not in watched_ids:
            break
    return id

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

    # user = create_user('WilliamTest2','unhashedpass')
    # users_collection.insert_one(user);
    # mongo.db.users.insert_one(user)

    selectedUser = users_collection.find_one({"username":"WilliamTest2"})

    if selectedUser:

        # print("User's date: " + selectedUser["daily_movie"]["recommended_date"].strftime("%Y %m %d"))
        # print("Computer's date: " + datetime.datetime.now().strftime("%Y %m %d"))
        # print("Equal?: "+ str(selectedUser["daily_movie"]["recommended_date"] == datetime.datetime.now()))

        # Checks if movie has been assigned for the day if last recommended movie date is same as today
        user_movie_id = selectedUser["daily_movie"]["movie_id"]
        user_recommended_date = selectedUser["daily_movie"]["recommended_date"]
        
        isAlreadyAssigned = user_recommended_date.strftime("%Y %m %d") == datetime.datetime.now().strftime("%Y %m %d")

        # if movie hasn't been assigned for the day, set a new movie id user hasn't seen before
        if not isAlreadyAssigned:
            new_movie_id = random_movie_id(selectedUser["watched_movies"])
            user_movie_id = new_movie_id
            user_recommended_date = datetime.datetime.now()

        selected_movie = g.all_movies[user_movie_id]

    movie_picked = True

    if not movie_picked:
        selected_movie = g.all_movies[random.randint(1,1000)]
    # for row in g.all_movies:
    #     print(row[1])
    return render_template("index.html", selectedMovie=selected_movie)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3000)