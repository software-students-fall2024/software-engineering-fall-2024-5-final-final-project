from flask import Blueprint  # type: ignore

routes = Blueprint("routes", __name__)


@routes.route("/")
def index():
    return "Welcome to our Personal Finance Tracker"
