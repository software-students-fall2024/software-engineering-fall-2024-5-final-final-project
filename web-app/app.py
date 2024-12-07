""" 
Web app frontend
"""

from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from database import db
from user.user import user, login_manager

app = Flask(__name__)
app.secret_key = "secret_key"  # needed for flask login sessions

login_manager.init_app(app)
app.register_blueprint(user, url_prefix="/user")


# @app.route("/")
# def home():
#     """Render main page"""
#     return render_template("index.html")


@app.route("/")
def index():
    """Redirect to right page if logged in or not"""
    if current_user.is_authenticated:
        return render_template("calendar.html")
    return redirect(url_for("user.login"))


@app.route("/signup")
def signup():
    """Render Signup page"""
    return render_template("Signup.html")


@login_required
@app.route("/menu")
def menu():
    """Render menu page"""
    return render_template("Menu.html")


@login_required
@app.route("/calendar")
def calendar():
    """Render calendar page"""
    return render_template("calendar.html")


@app.route("/analytics")
@login_required
def analytics():
    """Render Analytics page"""
    return render_template("Analytics.html")

@app.route("/search")
@login_required
def search():
    """Render Search page"""
    return render_template("Search.html")

@app.route("/user-info", methods=["GET", "POST"])
@login_required
def user_info():
    """Handle displaying and updating user information"""
    if request.method == "POST":
        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")

        db.users.update_one(
            {"email": current_user.email},
            {"$set": {"firstname": firstname, "lastname": lastname}}
        )

        return redirect(url_for("user_info"))

    user_data = db.users.find_one({"email": current_user.email})

    user_info = {
        "email": user_data["email"],
        "firstname": user_data.get("firstname", ""),
        "lastname": user_data.get("lastname", ""),
    }

    return render_template("edit-user-info.html", user_info=user_info)

@app.route("/delete-acct")
@login_required 
def delete_acct():
    return render_template("delete-acct.html")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
