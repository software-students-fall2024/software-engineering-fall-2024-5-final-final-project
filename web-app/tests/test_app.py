import pytest
from flask import session
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from app import app,users_collection, journal_collection

@pytest.fixture
def client():
    """
    Create a test client and set up the database for testing.
    """
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"
    with app.test_client() as client:
        with app.app_context():
            # Clear the test database
            users_collection.delete_many({})
            journal_collection.delete_many({})
        yield client

def test_index_redirect(client):
    """
    Test that the index route redirects to the login page.
    """
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.location

def test_register_user(client):
    """
    Test user registration.
    """
    response = client.post("/register", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302
    assert "/login" in response.location
    user = users_collection.find_one({"username": "testuser"})
    assert user is not None

def test_register_existing_user(client):
    """
    Test registration fails for an existing user.
    """
    users_collection.insert_one({"username": "testuser", "password": "hashedpass"})
    response = client.post("/register", data={"username": "testuser", "password": "testpass"}, follow_redirects=True)
    assert "Username already exists. Please choose another." in response.data.decode("utf-8")

def test_login_user(client):
    """
    Test user login.
    """
    users_collection.insert_one({
        "username": "testuser",
        "password": generate_password_hash("testpass", method="pbkdf2:sha256")
    })
    response = client.post("/login", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "user_id" in sess

def test_login_invalid_user(client):
    """
    Test login with invalid credentials.
    """
    response = client.post("/login", data={"username": "fakeuser", "password": "fakepass"}, follow_redirects=True)
    assert b"Invalid username or password" in response.data

def test_logout_user(client):
    """
    Test user logout.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "test_id"
    response = client.get("/logout", follow_redirects=True)
    assert "user_id" not in session
    assert b"You have been logged out" in response.data

def test_calendar_access(client):
    """
    Test calendar access for logged-in users.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "test_id"
    response = client.get("/calendar")
    assert response.status_code == 200

def test_calendar_redirect(client):
    """
    Test calendar redirection for non-logged-in users.
    """
    response = client.get("/calendar")
    assert response.status_code == 302
    assert "/login" in response.location

def test_journal_entry_add(client):
    """
    Test adding a journal entry.
    """
    with client.session_transaction() as sess:
        sess["user_id"] = "test_id"
    response = client.post("/journal/2023/12/1", data={"content": "Test entry"})
    assert response.status_code == 302
    entry = journal_collection.find_one({"user_id": "test_id", "date": "2023-12-01"})
    assert entry is not None
    assert entry["content"] == "Test entry"

def test_journal_entry_edit(client):
    """
    Test editing a journal entry.
    """
    journal_collection.insert_one({
        "user_id": "test_id",
        "date": "2023-12-01",
        "content": "Old content",
    })
    with client.session_transaction() as sess:
        sess["user_id"] = "test_id"
    response = client.post("/journal/2023/12/1", data={"content": "Updated content"})
    assert response.status_code == 302
    entry = journal_collection.find_one({"user_id": "test_id", "date": "2023-12-01"})
    assert entry["content"] == "Updated content"

def test_journal_entry_delete(client):
    """
    Test deleting a journal entry.
    """
    entry_id = journal_collection.insert_one({
        "user_id": "test_id",
        "date": "2023-12-01",
        "content": "To be deleted",
    }).inserted_id
    with client.session_transaction() as sess:
        sess["user_id"] = "test_id"
    response = client.post(f"/delete/{entry_id}", follow_redirects=True)
    assert response.status_code == 200
    entry = journal_collection.find_one({"_id": ObjectId(entry_id)})
    assert entry is None
