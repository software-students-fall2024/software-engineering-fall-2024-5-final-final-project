from flask import Flask, render_template, request, redirect, url_for
from craps_func import linebet, buybet

app = Flask(__name__)


@app.route("/")
def index():
    return redirect(url_for("craps_home", username="user"))


@app.route("/<username>/craps", methods = ["POST", "GET"])
def craps_home(username):
    return render_template("craps_home.html", username=username, balance="10000")


@app.route("/<username>/craps/playline", methods=["POST"])
def playline(username):
    win = True if request.form["bettype"] == 'p' else False
    bet = float(request.form["betamount"])
    balance = float(request.form["balance"])
    rolls, result = linebet(win)
    return_text= "Here are the rolls:\n"
    for r in rolls:
        return_text+=r + "\n"
    
    if result == 'w':
        return_text += "You win!"
        balance += bet
    elif result == 'l':
        return_text+= "You lost!"
        balance-=bet 
    else:
        return_text += "It was a tie!"

    # update database maybe use requests?
    # or maybe make a different .py that will make a request

    return render_template("craps_results.html", username=username, balance=balance, textResult=return_text)


@app.route("/<username>/craps/playbuy", methods=["POST"])
def playbuy(username):
    balance = 10000
    return render_template("craps_results.html", username=username, balance=balance)


if __name__ == "__main__":
    app.run()