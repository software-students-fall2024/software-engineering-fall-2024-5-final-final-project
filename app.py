from flask import Flask, render_template, request, redirect, flash, jsonify, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
import pymongo
import datetime
from bson.objectid import ObjectId
from bson import json_util
from datetime import datetime, time
import os

app = Flask(__name__)

app.secret_key = 'secret'

#mongodb connect
cxn = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = cxn[os.getenv("MONGO_DBNAME", "database")]
users = db['users']
events = db['events']

#Configure Flask-login
login_manager = LoginManager()
login_manager.init_app(app)

#define user
class User(UserMixin):
    def __init__(self, username):
        self.username = username

    def get_id(self):
        return self.username

user = None
@login_manager.user_loader
def load_user(user_id):
    user = users.find_one({"username": user_id})
    return User(username=user["username"]) if user else None

login_manager.user_loader(load_user)

try:
    cxn.admin.command("ping")
    print(" *", "Connected to MongoDB!")
except Exception as e:
    print(" * MongoDB connection error:", e)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        if users.find_one({'username': username}):
            flash('Username already exists. Choose a different one.', 'danger')
        else:
            users.insert_one({'username': username, 'password': password})
            flash('Registration successful. You can now log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username and password match
        user = users.find_one({'username': username, 'password': password})

        if user :
            user = User(user['username'])
            login_user(user)
            return redirect('/')
        else:
            flash('Invalid username or password.')

    return render_template('login.html')
    
@app.route('/api/status')
def status():
    return jsonify({'logged_in': current_user.is_authenticated}) 
    
@app.route('/logout')
@login_required
def logout():
    # Logout the user
    logout_user()
    return redirect('/login')
    
@app.route('/')
def home():
    """
    Route for the home page.
    Returns:
        rendered template (str): The rendered HTML template.
    """
    if not current_user.is_authenticated :
        flash("Login Required")
        return redirect('/login')
    return render_template("home.html")

@app.route('/event/add', methods=['GET', 'POST'])
@login_required
def add_event():
    if request.method == 'POST':
        name = request.form["fname"]
        description = request.form["fmessage"]
        hour = request.form["hours"]
        minute = request.form["minutes"]
        date = request.form["date"]

        datetime_str = datetime.strptime(date + " " + hour + ":" + minute, '%m/%d/%Y %H:%M')
        formatted_time = datetime_str.strftime('%Y-%m-%dT%H:%M:%S')

        doc = {
            "name": name,
            "description": description,
            "time": formatted_time,
            "user": current_user.username
        }
        events.insert_one(doc)

        return redirect(url_for("home"))
    return render_template('event-add.html')
    
@app.route('/database')
@login_required
def database():
    user_events = list(events.find({"user": current_user.username}))
    return jsonify(json_util.dumps(user_events))
    
@app.route('/event/<event_id>/edit', methods=['POST', 'GET'])
@login_required
def edit_event(event_id):
    """
    Route for POST requests to the edit page.
    Accepts the form submission data for the specified document and updates the document in the database.
    Args:
        post_id (str): The ID of the post to edit.
    Returns:
        Redirect (Response): A redirect response to the home page.
    """
    if request.method == 'GET':
        doc = events.find_one({"_id": ObjectId(event_id)})
        return render_template("item.html", doc=doc)

    name = request.form["fname"]
    description = request.form["fmessage"]
    hour = request.form["hours"]
    minute = request.form["minutes"]
    date = request.form["date"]

    datetime_str = datetime.strptime(date + " " + hour + ":" + minute, '%m/%d/%Y %H:%M')

    doc = {
        "name": name,
        "description": description,
        "time": datetime_str,
        "user": current_user.username
    }

    events.update_one({"_id": ObjectId(event_id)}, {"$set": doc})
    return redirect(url_for("home"))

@app.route('/event/<event_id>/time', methods=['POST'])
@login_required
def edit_time(event_id):
    start = request.form["start"]
    events.update_one({"_id": ObjectId(event_id)}, {"$set": {"time": start}})

    return redirect(url_for("home"))

@app.route('/event/<event_id>/delete', methods=['GET'])
def delete_event(event_id):
    """
    Route for GET requests to the delete page.
    Deletes the specified record from the database, and then redirects the browser to the home page.
    Args:
        post_id (str): The ID of the post to delete.
    Returns:
        redirect (Response): A redirect response to the home page.
    """
    events.delete_one({"_id": ObjectId(event_id)})
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=3000)