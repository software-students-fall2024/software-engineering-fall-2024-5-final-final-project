""" 
Web app frontend
"""

from flask import Flask, render_template
from flask_login import LoginManager
from user.auth import auth, login_manager

app = Flask(__name__)
app.secret_key = ""

login_manager.init_app(app)
app.register_blueprint(auth, url_prefix="/auth")  # routes that need auth prefixed with /auth


@app.route("/")
def home():
    """Render main page"""
    return render_template("main.html")


# write new functions here
if __name__ == "__main__":
    app.run(debug=True, port=8080)
