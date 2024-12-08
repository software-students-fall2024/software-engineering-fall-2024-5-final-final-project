import pytest
from flask import session
from bson import ObjectId
from app import app, col_users, col_groups

@pytest.fixture
def client():
    # Create a test client using the Flask application configured for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture
def test_user():
    # Insert a test user into the database
    user_id = ObjectId()
    col_users.insert_one({
        "_id": user_id,
        "name": "testuser",
        "password": b"somehashedpassword", 
        "groups": []
    })
    yield {"_id": user_id, "name": "testuser"}
    col_users.delete_one({"_id": user_id})

def login_user(client, username, password):
    # Simulate login by posting to the /login route
    return client.post("/login", data={
        "username": username,
        "password": password
    }, follow_redirects=True)

def test_home_logged_out(client):
    # Access /main without logging in should redirect to /login
    response = client.get("/main", follow_redirects=True)
    assert response.status_code == 200
    # The login page should mention "Login" or contain a login form
    assert b"Login" in response.data

def test_home_logged_in(client, test_user):
    with client.session_transaction() as sess:
        sess["username"] = test_user["name"]

    # Now user is 'logged in'
    response = client.get("/main", follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome to SplitSmart!" in response.data

def test_groups_no_login(client):
    # Try to access /groups without login
    response = client.get("/groups", follow_redirects=True)
    # Should redirect to login page
    assert response.status_code == 200
    assert b"Login" in response.data

def test_create_group_logged_out(client):
    # Try accessing /create-group without login
    response = client.get("/create-group", follow_redirects=True)
    assert response.status_code == 200
    # Since not logged in, should show login page or mention
    assert b"Login" in response.data

def test_create_group_logged_in(client, test_user):
    # Log in the test user
    with client.session_transaction() as sess:
        sess["username"] = test_user["name"]

    # Access the create group page after login
    response = client.get("/create-group")
    assert response.status_code == 200
    # Should show create group form
    assert b"create new group" in response.data.lower()

def test_add_expense_no_login(client):
    # Check if accessing add-expense without login redirects
    response = client.get("/add-expense", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_login_with_invalid_credentials(client):
    response = client.post("/login", data={
        "username": "nonexistent",
        "password": "wrongpassword"
    }, follow_redirects=True)
    # Should remain on login page with error message
    assert b"Username not found" in response.data or b"Invalid password" in response.data

