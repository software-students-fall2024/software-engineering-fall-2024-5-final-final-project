from flask import Flask, render_template, g;
import csv;
import os;
import random;

app = Flask(__name__)

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
    movie_picked = False
    if not movie_picked:
        selected_movie = g.all_movies[random.randint(1,1000)]
    # for row in g.all_movies:
    #     print(row[1])
    return render_template("index.html", selectedMovie=selected_movie)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)