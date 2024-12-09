"""
backend.main

This module initializes and runs the Flask application, providing a central point to configure and launch the backend services for the project.
"""

import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from backend.routes import routes  # pylint: disable=import-error
from backend.database import Database, User

db = Database()
login_manager = LoginManager()


def create_app():
    """
    Create and configure the Flask application.
    This function sets up essential configurations, middleware, routes, and third-party integrations like CORS and Flask-Login.
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
        Load a user from the database by their unique user ID.
        
        Args:
            user_id (str): The unique identifier for a user.
        
        Returns:
            User: The user object if found, otherwise None.
        """
        user_data = db.get_user_by_id(user_id)
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

    # Register existing routes
    app.register_blueprint(routes)

    # Add signup route
    @app.route("/api/signup", methods=["POST"])
    def signup():
        """
        Handle user signup requests.
        
        Expects JSON payload:
        {
            "username": "<username>",
            "password": "<password>"
        }
        
        Returns:
            JSON response indicating success or failure.
        """
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return (
                jsonify(
                    {"success": False, "message": "Username and password required"}
                ),
                400,
            )

        # Create a new user in the database
        created = db.create_user(username, password)
        if created:
            return (
                jsonify({"success": True, "message": "User created successfully"}),
                201,
            )
        return jsonify({"success": False, "message": "User already exists"}), 409

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5001)
