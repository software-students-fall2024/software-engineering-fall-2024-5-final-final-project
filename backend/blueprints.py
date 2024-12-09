"""
This module defines the Blueprint instances used across the application.
"""

from flask import Blueprint

# Create the routes blueprint that will be used by other modules
routes = Blueprint("routes", __name__)
