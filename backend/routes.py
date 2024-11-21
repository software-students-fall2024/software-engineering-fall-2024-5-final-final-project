"""
This file details each Flask route
"""

from flask import Blueprint  # type: ignore

routes = Blueprint("routes", __name__)


@routes.route("/")
def index():
    """Basic index route for now."""
    return "Welcome to our Personal Finance Tracker"
