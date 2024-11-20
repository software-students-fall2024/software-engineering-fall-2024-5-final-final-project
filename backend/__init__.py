from flask import Flask  # type: ignore
from backend import routes

# We'll configure MONGO URI later
# MONGO_URI = ""


def create_app():
    """Set up the Flask app."""
    app = Flask(__name__)

    # app.config["MONGO_URI"] = MONGO_URI

    app.register_blueprint(routes)

    return app
