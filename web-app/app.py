from flask import Flask, g;
import csv;
import os;

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
    for row in g.all_movies:
        print(row[1])
    return 'Hello World'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)