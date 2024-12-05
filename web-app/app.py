""" 
Web app frontend
"""

from flask import Flask, redirect, render_template, url_for
from flask_login import current_user, login_required
from user.auth import auth, login_manager

app = Flask(__name__)
app.secret_key = ""

login_manager.init_app(app)
app.register_blueprint(auth, url_prefix="/auth")  # routes that need auth prefixed with /auth


@app.route("/")
def index():
    """Redirect to right page if logged in or not"""
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("auth.login"))


@app.route("/")
@login_required
def home():
    """Render main page"""
    return render_template("index.html")


# write new functions here
if __name__ == "__main__":
    app.run(debug=True, port=8080)
