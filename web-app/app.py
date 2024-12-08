from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_login import current_user, login_required, logout_user
from database import db
from user.user import user, login_manager

def create_app():
    """App Factory Function"""
    app = Flask(__name__)
    app.secret_key = "secret_key"

    # Initialize Flask-Login
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(user, url_prefix="/user")

    # Define the index route inside the factory
    @app.route("/")
    def index():
        """Redirect to the appropriate page if logged in or not"""
        if current_user.is_authenticated:
            return render_template("calendar.html")
        return redirect(url_for("user.login"))

    return app


app = create_app()  # Use the factory function to create the app



@app.route("/user/delete-event/<event_id>", methods=["DELETE"])
@login_required
def delete_event(event_id):
    """Delete a user event by ID."""
    current_user.delete_event(db, event_id)
    return jsonify({"message": "Event deleted successfully"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)



@app.route("/signup")
def signup():
    """Render Signup page"""
    return render_template("Signup.html")


@app.route("/menu")
@login_required
def menu():
    """Render Menu page"""
    return render_template("Menu.html")


@app.route("/calendar")
@login_required
def calendar():
    """Render Calendar page"""
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
    """Render Delete Account page"""
    return render_template("delete-acct.html")


@app.route("/logout")
def logout():
    """Log out the user and redirect to the login page"""
    logout_user()
    return redirect(url_for("user.login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
