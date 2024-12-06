"""
backend.main

This module initializes and runs the Flask application.
"""

import os
from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from backend.routes import routes  # pylint: disable=import-error
from backend.database import Database, User

db = Database()
login_manager = LoginManager()


def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-here")

    # Initialize LoginManager
    login_manager.init_app(app)
    login_manager.login_view = "routes.login"  # Redirect to login page if not logged in

    # User loader function
    @login_manager.user_loader
    def load_user(user_id):
        """
        Load a user from the database by their username.
        """
        user_data = db.get_user_by_id(ObjectId(user_id))
        if user_data:
            return User(user_data)
        return None

    CORS(
        app,
        supports_credentials=True,
        origins=["http://localhost:5000", "http://frontend:5000"],
        allow_headers=["Content-Type"],
        expose_headers=["Set-Cookie"],
    )
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = False
    app.register_blueprint(routes)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
