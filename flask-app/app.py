# Import necessary pkgs
import flask
from flask import Flask, render_template, request, redirect, url_for

# Instantiate flask app, create key
app = Flask(__name__)
app.secret_key = "letsgogambling"

# Simulated database of users
users = {'abc': {'password': 'xyz'}, 'zyx': {'password': 'cba'}}

@app.route("/")
def redirect_home():
    return redirect(url_for('show_home'))

@app.route("/userhome")
def show_home():
    return render_template("user_home.html")

if __name__ == "__main__":
    app.run(debug=True)
