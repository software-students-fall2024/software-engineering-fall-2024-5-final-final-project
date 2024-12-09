import pytest
from app import app, get_weather, seed_database, get_outfit_from_db
from unittest.mock import patch, MagicMock
from flask import url_for
from werkzeug.security import generate_password_hash

# Fixtures
@pytest.fixture
def client():
    """Set up a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Test: `get_weather`
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


# Test: Index route
def test_index(client):
    """Test index route."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"index.html" in response.data


# Test: Fetch Weather Route
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


def test_register(client):
    response = client.post('/register', data={
        'username': 'testuser',
        'password': 'testpassword',
        'repassword': 'testpassword',
        'gender': 'male'
    })
    assert response.status_code == 302  # Redirects to login
    assert b"Registration successful" in response.data

def test_login_success(client):
    with patch('app.db.users.find_one', return_value={
        "username": "testuser",
        "password": generate_password_hash("testpassword"),
        "gender": "male"
    }):
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        })
        assert response.status_code == 302  # Redirects to index
        assert b"Login successful" in response.data

def test_logout(client):
    with client.session_transaction() as session:
        session['user_id'] = 'test_user_id'
    response = client.get('/logout')
    assert response.status_code == 302  # Redirects to login
    assert b"You have been logged out" in response.data


def test_add_location(client):
    with patch('app.db.locations.update_one') as mock_update:
        response = client.post('/add_location', json={"location": "New York"})
        assert response.status_code == 200
        json_data = response.get_json()
        assert json_data["success"] is True

def test_get_locations(client):
    with patch('app.db.locations.find_one', return_value={"locations": ["New York", "Los Angeles"]}):
        response = client.get('/get_locations')
        assert response.status_code == 200
        json_data = response.get_json()
        assert "New York" in json_data
        assert "Los Angeles" in json_data

@patch('app.os.path.exists', return_value=True)
@patch('app.db.outfits.insert_many')
def test_seed_database(mock_insert, mock_exists):
    mock_insert.return_value = MagicMock()
    seed_database()
    assert mock_insert.called

@patch('app.db.outfits.find_one', return_value={
    "image_url": "/static/images/cold/male/jacket.png",
    "description": "A warm jacket"
})
def test_get_outfit_from_db(mock_find_one):
    outfit = get_outfit_from_db(-5, "male")
    assert outfit["image"] == "/static/images/cold/male/jacket.png"
    assert outfit["description"] == "A warm jacket"

@patch('app.get_weather')
def test_get_weather_data_success(mock_get_weather, client):
    mock_get_weather.return_value = (10, 'cloudy')
    response = client.post('/get_weather_data', json={"city": "Chicago"})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['city'] == "Chicago"
    assert json_data['temperature'] == "10°C"
    assert json_data['description'] == "cloudy"
