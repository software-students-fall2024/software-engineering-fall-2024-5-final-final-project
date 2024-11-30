import os
from flask import Flask, render_template
from pymongo import MongoClient

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET')  

    mongodb_username = os.getenv('MONGODB_USERNAME') 
    mongodb_password = os.getenv('MONGODB_PASSWORD')

    db_uri = f"mongodb://{mongodb_username}:{mongodb_password}@mongodb:27017"
    client = MongoClient(db_uri)

    @app.route('/')
    def index():
        return render_template('index.html')
    return app

if __name__ == "__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", "8080")
    app = create_app()
    app.run(port=FLASK_PORT)