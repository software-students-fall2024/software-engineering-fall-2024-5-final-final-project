import sys
import os
from bson.objectid import ObjectId
from unittest.mock import patch, MagicMock
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), "../web-app"))

from app import app, get_weather, seed_database, get_outfit_from_db

@pytest.fixture
def client():
    """Set up a test client for the Flask app."""
    app.config['TESTING'] = True
    app.config["LOGIN_DISABLED"] = False
    with app.test_client() as client:
        yield client
