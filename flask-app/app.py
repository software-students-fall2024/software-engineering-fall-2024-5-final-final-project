"""
Module: a Flask application that serves as the
interface for our gambling application, using
flask-login to initialize user data storage
"""

# import necessary pkgs
from flask import Flask, render_template, request, redirect, url_for, jsonify
import flask_login
from flask_login import login_user, logout_user, login_required
from craps_func import linebet, buybet
import db

# instantiate flask app, create key
app = Flask(__name__)
app.secret_key = "letsgogambling"

# setup flask login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

# simulate database of users, placeholder until pymongo connection
db.register_user("abc", "xyz")
users = db.get_users()
# users = {}
# users["abc"] = {"password": "xyz"}

users_balance = {'abc': 500,
                 'zyx': 900}

# create User object
class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(username):
    if username not in users:
        return
    
    user = User()
    user.id = username
    return user

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    if username not in users:
        return
    
    user = User()
    user.id = username
    return user
    
@app.route("/")
def redirect_home():
    return redirect(url_for('show_login'))

@app.route("/login_screen", methods = ["GET","POST"])
def show_login():

    error_msg = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # error handling for missing/incorrect values
        if username in users and password == users[username]['password']:
            user = User()
            user.id = username
            flask_login.login_user(user)
            return redirect(url_for('user_home', username=username))        
        else:
            error_msg = "Invalid credentials, please try again."

    return render_template('login.html', error_msg=error_msg)

@app.route('/<username>')
@flask_login.login_required
def user_home(username):
    # if username in users_balance:
    #     user_balance = users_balance[username]['balance']
    #     return render_template('user_home.html', username=username, balance = user_balance)
    user_balance = db.get_bal(username)
    return render_template('user_home.html', username=username, balance = user_balance)
    
@app.route("/<username>/craps", methods = ["POST", "GET"])
@flask_login.login_required
def craps_home(username):
    balance = request.form['balance']
    return render_template("craps_home.html", username=username, balance=balance)


@app.route("/<username>/craps/playline", methods=["POST"])
@flask_login.login_required
def playline(username):
    win = True if request.form["bettype"] == 'p' else False
    bet = float(request.form["betamount"])
    balance = float(request.form["balance"])
    rolls, result = linebet(win)
    #return_text= "Here are the rolls:\n"
    return_text = ""
    for r in rolls:
        return_text+=r + "@"
    
    win = False
    if result == 'w':
        return_text += "You win!"
        balance += bet
        win = True
    elif result == 'l':
        return_text+= "You lost!"
        balance-=bet 
    else:
        return_text += "It was a tie!"

    db.update_bal(username, balance, win, "craps")

    # update database maybe use requests?
    # or maybe make a different .py that will make a request

    return render_template("craps_results.html", username=username, balance=balance, textResult=return_text)


@app.route("/<username>/craps/playbuy", methods=["POST"])
@flask_login.login_required
def playbuy(username):
    win = True if request.form["bettype"] == 'b' else False
    bet = float(request.form["betamount"])
    place = int(request.form["buynum"])
    balance = float(request.form["balance"])
    rolls, result, odds = buybet(win, place)
    return_text= ""
    win = False
    for r in rolls:
        return_text+=r + "@"
    if result == 'w':
        return_text += "You win!"
        balance += bet * odds
        win = True
    elif result == 'l':
        return_text+= "You lost!"
        balance-=bet 

    db.update_bal(username, balance, win, "craps")
    
    return render_template("craps_results.html", username=username, balance=balance, textResult=return_text)


@app.route('/logout', methods = ["GET", "POST"])
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect(url_for('show_login'))

@login_manager.unauthorized_handler
def unauthorized_handler():
    return 'Unauthorized', 401


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
