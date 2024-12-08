import pytest
from flask import json
from app import app

@pytest.fixture
def client():
    """
    Creates a test client for the Flask app.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
