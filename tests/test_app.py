import sys
import os
from bson.objectid import ObjectId
from unittest.mock import patch, MagicMock
import pytest

# Add web-app directory to sys.path
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
    "gender": "male"
})
@patch('app.check_password_hash', return_value=True)
def test_login_success(mock_hash, mock_find_one, client):
    """Test successful login."""
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Locations" in response.data  # Check for the redirected page content


def test_logout(client):
    """Test user logout."""
    with client.session_transaction() as session:
        session['_user_id'] = str(ObjectId())  # Simulate user login
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Don't have an account? Sign up Here" in response.data  # Match rendered content

@patch('app.current_user')
@patch('app.db.locations.update_one')
@patch('app.login_required', lambda x: x)  # Bypass @login_required decorator
def test_add_location(mock_update, mock_current_user, client):
    """Test adding a location."""
    mock_current_user.username = "testuser"  # Mock authenticated user
    with client.session_transaction() as session:
        session['_user_id'] = str(ObjectId())  # Simulate session
    
    response = client.post('/add_location', json={"location": "New York"}, follow_redirects=True)
    assert response.status_code == 200  # Expect successful response
    mock_update.assert_called_once_with(
        {"username": "testuser"},
        {"$addToSet": {"locations": "New York"}},
        upsert=True
    )


@patch('app.os.listdir', return_value=['jacket.png', 'coat.png'])
@patch('app.os.path.exists', return_value=True)  # Assume all paths exist
@patch('app.db.outfits.insert_many')
def test_seed_database(mock_insert, mock_exists, mock_listdir):
    """Test database seeding."""
    expected_data = [
        {
            "temperature_range_min": -100,
            "temperature_range_max": 0,
            "weather_condition": "cold",
            "gender": "male",
            "image_url": "/static/images/cold/male/jacket.png"
        },
        {
            "temperature_range_min": -100,
            "temperature_range_max": 0,
            "weather_condition": "cold",
            "gender": "male",
            "image_url": "/static/images/cold/male/coat.png"
        }
    ]
    seed_database()
    mock_insert.assert_called_once_with(expected_data)  # Check the mock was called with correct data


@patch('app.os.path.exists', return_value=False)  # Assume no folders exist
@patch('app.db.outfits.insert_many')
def test_seed_database_no_folders(mock_insert, mock_exists):
    seed_database()
    mock_insert.assert_not_called()  # Nothing to insert

@patch('app.db.users.find_one', return_value=None)
@patch('app.db.users.insert_one')
def test_register_success(mock_insert_one, mock_find_one, client):
    """Test user registration success."""
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword',
        'repassword': 'newpassword',
        'gender': 'male'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data
    mock_insert_one.assert_called_once()


@patch('app.db.users.find_one', return_value={"username": "existinguser"})
def test_register_failure_user_exists(mock_find_one, client):
    """Test user registration failure when username already exists."""
    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'password',
        'repassword': 'password',
        'gender': 'male'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Username already exists" in response.data

@patch('app.get_weather', return_value=(25, "sunny"))
def test_fetch_weather_success(mock_get_weather, client):
    """Test successful weather fetching."""
    response = client.get('/get_weather?city=New York')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['city'] == 'New York'
    assert json_data['temperature'] == '25°C'
    assert json_data['description'] == 'sunny'


@patch('app.get_weather', return_value=(None, None))
def test_fetch_weather_failure(mock_get_weather, client):
    """Test failed weather fetching."""
    response = client.get('/get_weather?city=InvalidCity')
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['error'] == "Could not fetch weather data"

@patch('app.db.outfits.find', return_value=[
    {"image_url": "/static/images/cold/male/jacket.png", "description": "A warm jacket"}
])
def test_get_outfit_from_db_success(mock_find):
    """Test fetching an outfit from the database."""
    outfit = get_outfit_from_db(-5, "male")
    assert outfit["image"] == "/static/images/cold/male/jacket.png"
    assert outfit["description"] == "Outfit for this temperature range"


@patch('app.db.outfits.find', return_value=[])
def test_get_outfit_from_db_no_outfit(mock_find):
    """Test fetching an outfit when none exists in the database."""
    outfit = get_outfit_from_db(-5, "male")
    assert outfit["image"] == "/images/default.png"
    assert outfit["description"] == "Default Outfit"

def test_locations_route(client):
    """Test the locations route."""
    with client.session_transaction() as session:
        session['_user_id'] = str(ObjectId())  # Simulate user login
    response = client.get('/locations')
    assert response.status_code == 200
    assert b"Add Locations" in response.data  # Adjust based on template content
