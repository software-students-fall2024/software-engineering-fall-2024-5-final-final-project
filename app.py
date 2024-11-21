from flask import Flask, render_template, request, redirect, url_for
import pymongo
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    
    app = Flask(__name__)

    cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
    db = cxn[os.getenv("MONGO_DBNAME")]

    try:
        cxn.admin.command("ping")
        print(" *", "Connected to MongoDB!")
    except Exception as e:
        print(" * MongoDB connection error:", e)
    
    @app.route("/")
    def home():
        """
        Route for the home page
        """
        return render_template("index.html")

    return app

if __name__ =="__main__":
    FLASK_PORT = os.getenv("FLASK_PORT", 5001)
    app = create_app()
    app.run(port=FLASK_PORT)