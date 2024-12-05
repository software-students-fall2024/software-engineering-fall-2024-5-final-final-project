import os
import subprocess
from flask import Flask, render_template, request, flash, redirect, send_file, url_for, session
from pymongo import MongoClient

def create_app():
    # app initialization
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    # database initialization
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["resume_db"]
    users_collection = db["users"]
    resumes_collection = db["resumes"]

    # home
    @app.route("/")
    def home():
        return render_template("home.html")

    # login
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            user = users_collection.find_one({"email": email, "password": password})
            if user:
                session["email"] = email
                flash("Login successful.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid email or password. Please try again.", "danger")
        return render_template("login.html")

    # register
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            if users_collection.find_one({"email": email}):
                flash("Email already registered. Choose a different one.", "danger")
            else:
                users_collection.insert_one({"email": email, "password": password})
                flash("Registration successful. You can now log in.", "success")
                return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard():
        if "email" in session:
            email = session["email"]
            resumes = resumes_collection.find({"email": email})
            return render_template("dashboard.html", email=email, resumes=resumes)
        else:
            flash("You must be logged in to access the dashboard.", "danger")
            return redirect(url_for("login"))
    
    @app.route("/logout")
    def logout():
        session.pop("email", None)
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))
    
    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5002, debug=True)
