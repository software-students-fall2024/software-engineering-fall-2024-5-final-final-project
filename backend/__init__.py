"""
This file initializes the Flask app
"""

from flask import Flask  # type: ignore
from backend.routes import routes

def create_app():
    """Set up the Flask app."""
    app = Flask(__name__)

    # app.config["MONGO_URI"] = MONGO_URI

    app.register_blueprint(routes)

    return app
