import pytest
import bcrypt
from app import app, users_collection


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_registration_existing_user(client):
    users_collection.insert_one({
        'username': 'existinguser',
        'password': bcrypt.hashpw(b'password', bcrypt.gensalt())
    })
    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

    users_collection.delete_one({'username': 'existinguser'})


def test_login_failure(client):
    response = client.post('/login', data={
        'username': 'nonexistentuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_profile_access_without_login(client):
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page" in response.data


def test_profile_access_with_login(client):
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/profile')
    assert response.status_code == 200
    assert b"Username already exists" in response.data

    users_collection.delete_one({"username": "existinguser"})


def test_logout(client):
    """Test logout functionality."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_profile_without_login(client):
    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page" in response.data
    

def test_unsave_recipe(client):
    """Test unsaving a recipe."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'
    response = client.get('/search', follow_redirects=True)

    assert response.status_code == 200

    user = users_collection.find_one({"username": "testuser"})
    assert not any(r['recipe_id'] == 'recipe123' for r in user["saved_recipes"])

    users_collection.delete_one({"username": "testuser"})


def test_profile_page(client):
    """Test profile page updates."""
    with client.session_transaction() as sess:
        flashes = sess['_flashes']
        assert any("Your pantry is empty" in msg for category, msg in flashes)
