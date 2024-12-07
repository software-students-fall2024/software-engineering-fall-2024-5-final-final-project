from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required
from user.models import User
from database import db

auth = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    user_data = User.find_by_email(db, user_id)
    if user_data:
        return User(email=user_data["email"])
    return None


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.validate_login(db, email, password)
        if user:
            login_user(user)
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password. Try again.", "error")
    return render_template("Login.html")


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]

        existing_user = User.find_by_email(db, email)
        if existing_user:
            flash("An account with that email already exists!", "error")
        else:
            User.create_user(db, email, password, firstname, lastname)
            return redirect(url_for("auth.login"))
    return render_template("Signup.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))
