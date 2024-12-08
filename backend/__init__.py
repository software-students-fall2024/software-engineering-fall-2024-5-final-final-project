"""
This file initializes the Flask app
"""

from flask import Flask
from flask_login import LoginManager
from backend.routes import routes


def create_app():
    """Set up the Flask app."""
    app = Flask(__name__)
    app.secret_key = "your-secret-key-here"  # Ensure this is set securely

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "routes.login"  # Redirect here if @login_required fails

    app.register_blueprint(routes)

    return app
