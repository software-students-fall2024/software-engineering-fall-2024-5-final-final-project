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


@patch('app.requests.get')
def test_get_weather_success(mock_get):
    """Test successful weather data retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        'main': {'temp': 25},
        'weather': [{'description': 'clear sky'}]
    }
    mock_get.return_value = mock_response

    temperature, description = get_weather('New York', 'test_api_key')
    assert temperature == 25
    assert description == 'clear sky'


@patch('app.requests.get')
def test_get_weather_failure(mock_get):
    """Test failed weather data retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    temperature, description = get_weather('InvalidCity', 'test_api_key')
    assert temperature is None
    assert description is None


@patch('app.db.users.find_one', return_value={
    "_id": ObjectId(),
    "username": "testuser",
    "password": "hashedpassword",
    "gender": "male"})
