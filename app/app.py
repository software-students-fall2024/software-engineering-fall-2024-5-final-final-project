from flask import Flask, render_template
from pymongo import MongoClient
from flask_login import UserMixin

def create_app():

    app = Flask(__name__)
    client = MongoClient("mongodb://mongodb:27017/")

    db = client.resume_db

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/login", methods = ['GET', 'POST'])
    def login():
        return render_template("login.html")
    
    @app.route("/register", methods = ['POST', 'GET'])
    def register():
        return render_template("register.html")
    
    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5002, debug=True)
