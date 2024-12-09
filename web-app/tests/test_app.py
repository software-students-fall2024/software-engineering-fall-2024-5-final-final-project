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
    "gender": "male"
})
# @patch('app.check_password_hash', return_value=True)
# def test_login_success(mock_hash, mock_find_one, client):
#     """Test successful login."""
#     response = client.post('/login', data={
#         'username': 'testuser',
#         'password': 'testpassword'
#     }, follow_redirects=True)
#     assert response.status_code == 200
#     assert b"Locations" in response.data  # Check for the redirected page content


def test_logout(client):
    """Test user logout."""
    with client.session_transaction() as session:
        session['_user_id'] = str(ObjectId())  # Simulate user login
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Don't have an account? Sign up Here" in response.data  # Match rendered content

@patch('app.os.path.exists', return_value=False)  # Assume no folders exist
@patch('app.db.outfits.insert_many')
def test_seed_database_no_folders(mock_insert, mock_exists):
    seed_database()
    mock_insert.assert_not_called()  # Nothing to insert

def test_register_page(client):
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Create" in response.data  # Check for the page title


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"User Login" in response.data


def test_index_redirect(client):
    response = client.get('/', follow_redirects=False)
    assert response.status_code == 302  # Redirect to login

@patch('app.db.users.find_one', return_value=None)  # Simulate no existing user
@patch('app.db.users.insert_one')
def test_register_success(mock_insert, mock_find, client):
    """Test successful registration."""
    response = client.post('/register', data={
        "username": "newuser",
        "password": "password123",
        "repassword": "password123",
        "gender": "male"
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"account" in response.data


# @patch('app.db.users.find_one', return_value={"username": "existinguser"})
# def test_register_existing_user(mock_find, client):
#     """Test registration with an existing username."""
#     response = client.post('/register', data={
#         "username": "existinguser",
#         "password": "password123",
#         "repassword": "password123",
#         "gender": "female"
#     }, follow_redirects=True)
#     assert response.status_code == 200
#     assert b"Username already exists." in response.data

@patch('app.db.users.find_one', return_value=None)  # User not found
def test_login_invalid_username(mock_find, client):
    """Test login with invalid username."""
    response = client.post('/login', data={"username": "wronguser", "password": "password123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


@patch('app.db.users.find_one', return_value={"username": "testuser", "password": "hashedpassword"})
@patch('app.check_password_hash', return_value=False)  # Incorrect password
def test_login_invalid_password(mock_check, mock_find, client):
    """Test login with incorrect password."""
    response = client.post('/login', data={"username": "testuser", "password": "wrongpassword"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data

@patch('app.get_weather', return_value=(15, "cloudy"))
@patch('app.get_outfit_from_db', return_value={"image": "image.jpg", "description": "A warm jacket"})
@patch('flask_login.current_user', autospec=True)  # Correct namespace for mocking
def test_index_with_weather(mock_user, mock_outfit, mock_weather, client):
    """Test index route with valid weather data."""
    mock_user.is_authenticated = True
    mock_user.username = "testuser"
    mock_user.gender = "male"

    response = client.get('/', query_string={"city": "New York"}, follow_redirects=True)
    assert response.status_code == 200

#371-383
@patch('app.db')  # Patch the entire db object
@patch('app.os.path.exists', return_value=True)
@patch('app.os.listdir', return_value=['jacket.png'])
def test_seed_database_with_data(mock_listdir, mock_exists, mock_db):
    """Test database seeding with valid data."""
    mock_insert = mock_db.outfits.insert_many  # Mock insert_many on the db object
    seed_database()
    print(f"Insert called: {mock_insert.called}")
    mock_insert.assert_called_once()



@patch('app.os.listdir', return_value=[])
@patch('app.os.path.exists', return_value=False)
@patch('app.db.outfits.insert_many')
def test_seed_database_no_data(mock_insert, mock_exists, mock_listdir):
    """Test database seeding when no folders exist."""
    seed_database()
    mock_insert.assert_not_called()

def test_login_missing_username(client):
    """Test login with missing username."""
    response = client.post('/login', data={"username": "", "password": "password123"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data


def test_login_missing_password(client):
    """Test login with missing password."""
    response = client.post('/login', data={"username": "testuser", "password": ""}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password." in response.data

def test_register_page_render(client):
    """Test rendering of the registration page."""
    response = client.get('/register')
    assert response.status_code == 200
    assert b"Sign Up" in response.data  # Check for the register form heading

def test_register_password_mismatch(client):
    """Test registration when passwords do not match."""
    response = client.post('/register', data={
        "username": "newuser",
        "password": "password123",
        "repassword": "password321",  # Mismatched passwords
        "gender": "male"
    }, follow_redirects=True)

    # Validate that the error message is displayed
    assert response.status_code == 200  # Renders the registration page again
    assert b"Passwords do not match." in response.data

#########


