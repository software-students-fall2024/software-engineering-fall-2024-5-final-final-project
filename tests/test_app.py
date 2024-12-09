import pytest
from app import app, get_weather
from unittest.mock import patch, MagicMock
from flask import url_for


@pytest.fixture
def client():
    """Set up a test client for the Flask app."""
    app.config['TESTING'] = True
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



def test_index(client):
    """Test index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"index.html" in response.data



@patch('app.get_weather')
def test_fetch_weather_success(mock_get_weather, client):
    """Test /get_weather route with valid city."""
    mock_get_weather.return_value = (22, 'sunny')
    response = client.get('/get_weather?city=Los Angeles')

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['city'] == 'Los Angeles'
    assert json_data['temperature'] == '22°C'
    assert json_data['description'] == 'sunny'


@patch('app.get_weather')
def test_fetch_weather_failure(mock_get_weather, client):
    """Test /get_weather route with invalid city."""
    mock_get_weather.return_value = (None, None)
    response = client.get('/get_weather?city=InvalidCity')

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Could not fetch weather data"
