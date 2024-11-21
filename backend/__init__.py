"""
This file initializes the Flask app
"""

from flask import Flask  # type: ignore
from backend.routes import routes

# We'll finish the configuration f MONGO URI later
# MONGO_URI = ""


def create_app():
    """Set up the Flask app."""
    app = Flask(__name__)

    # app.config["MONGO_URI"] = MONGO_URI

    app.register_blueprint(routes)

    return app
