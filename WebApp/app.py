
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import bcrypt
from pymongo import MongoClient

app = Flask(__name__)


mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
#Setup database for users
db = client['p5_user_database']
users_collection = db['p5_users']

#user authentication using session
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    if 'username' in session:
        return redirect('/') 
    return render_template('login.html')

#Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = users_collection.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['username'] = username 
        return jsonify(message="Login successful!"), 200
    else:
        return jsonify(message="Invalid username or password."), 401

# Signup
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify(message="Username already exists."), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    users_collection.insert_one({
        'username': username,
        'email': email,
        'password': hashed_password
    })

    return jsonify(message="Signup successful!"), 201



if __name__ == '__main__':
    app.run(debug=True)