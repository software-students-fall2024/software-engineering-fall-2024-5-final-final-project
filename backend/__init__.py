"""
This module initializes the Flask app and sets up configurations,
such as the CORS and login manager.
"""

from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS

login_manager = LoginManager()


def create_app():
    """
    Create and configure the Flask application.
    Returns:
        Flask app instance.
    """
    app = Flask(__name__)
    app.secret_key = "your-secret-key-here"

    # Configure session cookie settings
    app.config["SESSION_COOKIE_PATH"] = "/"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False

    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5000", "http://frontend:5000"],
    )

    login_manager.init_app(app)

    from backend.routes import routes  # pylint: disable=import-outside-toplevel

    app.register_blueprint(routes)

    return app
