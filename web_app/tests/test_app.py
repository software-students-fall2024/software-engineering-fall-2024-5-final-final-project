import pytest
import bcrypt
from app import app, users_collection


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_login_success(client):
    """Test successful login."""
    password = b"testpassword"
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    users_collection.insert_one({
        "username": "testuser",
        "password": hashed_password
    })

    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome" in response.data

    users_collection.delete_one({"username": "testuser"})


def test_login_failure(client):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'username': 'nonexistentuser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_register_success(client):
    """Test successful registration."""
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

    users_collection.delete_one({"username": "newuser"})


def test_register_existing_user(client):
    """Test registration with an existing username."""
    users_collection.insert_one({
        "username": "existinguser",
        "password": bcrypt.hashpw(b"password", bcrypt.gensalt())
    })

    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'newpassword'
    }, follow_redirects=True)
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


def test_add_pantry_item(client):
    """Test adding an item to the pantry."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    users_collection.insert_one({"username": "testuser", "pantry": []})

    response = client.post('/pantry', data={"ingredient": "tomato"}, follow_redirects=True)
    assert response.status_code == 200

    user = users_collection.find_one({"username": "testuser"})
    assert "tomato" in user["pantry"]

    users_collection.delete_one({"username": "testuser"})


def test_remove_pantry_item(client):
    """Test removing an item from the pantry."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    users_collection.insert_one({"username": "testuser", "pantry": ["onion"]})

    response = client.post('/pantry/delete', data={"ingredient": "onion"}, follow_redirects=True)
    assert response.status_code == 200

    user = users_collection.find_one({"username": "testuser"})
    assert "onion" not in user["pantry"]

    users_collection.delete_one({"username": "testuser"})


def test_save_recipe(client):
    """Test saving a recipe."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    users_collection.insert_one({"username": "testuser", "saved_recipes": []})

    recipe_data = {
        'recipe_id': 'recipe123',
        'name': 'Test Recipe',
        'image': 'test.jpg',
        'source': 'Test Source',
        'url': 'http://test.com'
    }
    response = client.post('/save_recipe', json=recipe_data)
    assert response.status_code == 200
    assert b"Recipe saved successfully" in response.data

    user = users_collection.find_one({"username": "testuser"})
    assert any(r['recipe_id'] == 'recipe123' for r in user["saved_recipes"])

    users_collection.delete_one({"username": "testuser"})


def test_unsave_recipe(client):
    """Test unsaving a recipe."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    users_collection.insert_one({"username": "testuser", "saved_recipes": [{
        'recipe_id': 'recipe123',
        'name': 'Test Recipe'
    }]})

    response = client.post('/unsave_recipe', data={"recipe_id": "recipe123"}, follow_redirects=True)
    assert response.status_code == 200

    user = users_collection.find_one({"username": "testuser"})
    assert not any(r['recipe_id'] == 'recipe123' for r in user["saved_recipes"])

    users_collection.delete_one({"username": "testuser"})


def test_profile_page(client):
    """Test profile page updates."""
    with client.session_transaction() as sess:
        sess['username'] = 'testuser'

    users_collection.insert_one({"username": "testuser", "dietary_restrictions": []})

    response = client.post('/profile', data={"restrictions": ["vegan", "gluten-free"]}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dietary restrictions updated successfully" in response.data

    user = users_collection.find_one({"username": "testuser"})
    assert "vegan" in user["dietary_restrictions"]
    assert "gluten-free" in user["dietary_restrictions"]

    users_collection.delete_one({"username": "testuser"})
