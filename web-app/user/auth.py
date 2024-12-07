from flask import Blueprint, request, redirect, url_for, render_template, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from flask_bcrypt import Bcrypt
from database import db

auth = Blueprint("auth", __name__)
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = "auth.login"

class User(UserMixin):
    def __init__(self, email, password=None, firstname=None, lastname=None):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.id = email # no username, just use email

    @staticmethod
    def find_by_email(db, email):
        return db.users.find_one({"email": email})

    @staticmethod
    def create_user(db, email, password, firstname, lastname):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_data = {
            "email": email,
            "password": hashed_password,
            "firstname": firstname,
            "lastname": lastname,
        }
        return db.users.insert_one(user_data)

    @staticmethod
    def validate_login(db, email, password):
        user = db.users.find_one({"email": email})
        if user and bcrypt.check_password_hash(user['password'], password):
            return User(
                email=user["email"],
                password=user["password"],
                firstname=user.get("firstname"),
                lastname=user.get("lastname"),
            )
        return None

@login_manager.user_loader
def load_user(user_id):
    user_data = User.find_by_email(db, user_id)
    if user_data:
        return User(email=user_data["email"])
    return None

# auth routes
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

@auth.route('/delete-acct', methods=['POST', 'GET'])
@login_required
def delete_account():
    """Delete the logged-in user's account."""
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')

        if email == current_user.email:
            user = db.users.find_one({"email": email})

            if user and bcrypt.check_password_hash(user['password'], password):
                db.users.delete_one({"email": email})

                logout_user()

                flash('Your account has been successfully deleted.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Invalid email or password. Please try again.', 'error')
        else:
            flash('The provided email does not match the current user.', 'error')

    return render_template('delete-acct.html')

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))
