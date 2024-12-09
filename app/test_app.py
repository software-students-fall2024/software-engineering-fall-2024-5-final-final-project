import os
import pytest
import mongomock
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime
from flask import session
from app import app, db, users_collection, posts_collection, fs
from werkzeug.security import generate_password_hash
from io import BytesIO

@pytest.fixture
def flask_client():
    """
    Provide a Flask test client for testing application routes.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db(monkeypatch):
    """
    Mock the database with mongomock and gridfs.
    """
    mock_db = mongomock.MongoClient().db

    # Mock collections
    mock_users = mock_db.users
    mock_posts = mock_db.posts

    # Mock fs
    fs_mock = MagicMock()
    fs_mock.put.return_value = ObjectId()
    fs_mock.get.return_value.read.return_value = b"image_data"
    fs_mock.get.return_value.content_type = "image/png"

    # Patch references in the app
    monkeypatch.setattr("app.db", mock_db)
    monkeypatch.setattr("app.users_collection", mock_users)
    monkeypatch.setattr("app.posts_collection", mock_posts)
    monkeypatch.setattr("app.fs", fs_mock)

    return mock_db

def login(flask_client, username="testuser", user_id=None):
    with flask_client.session_transaction() as sess:
        sess['user_id'] = str(user_id if user_id else ObjectId())

def test_register_success(flask_client, mock_db):
    """
    Test successful user registration.
    """
    response = flask_client.post(
        "/register",
        data={"username": "new_user", "password1": "password", "password2": "password"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b'login' in response.data
    assert mock_db.users.find_one({"username": "new_user"}) is not None

def test_register_password_mismatch(flask_client, mock_db):
    """
    Test registration when passwords do not match.
    """
    response = flask_client.post(
        "/register",
        data={"username": "another_user", "password1": "pass", "password2": "fail"},
        follow_redirects=True,
    )
    assert b"Passwords do not match" in response.data
    assert mock_db.users.find_one({"username": "another_user"}) is None

def test_register_existing_user(flask_client, mock_db):
    """
    Test registering with an existing username.
    """
    mock_db.users.insert_one({"username": "testuser", "password": "hashed"})
    response = flask_client.post(
        "/register",
        data={"username": "testuser", "password1": "pass", "password2": "pass"},
        follow_redirects=True,
    )
    assert b"Username already exists" in response.data

def test_login_invalid_credentials(flask_client, mock_db):
    """
    Test login with invalid credentials.
    """
    response = flask_client.post(
        "/login",
        data={"username": "no_user", "password": "none"},
        follow_redirects=True
    )
    assert b"Invalid username or password" in response.data

def test_login_success(flask_client, mock_db):
    """
    Test login with valid credentials.
    """
    mock_db.users.insert_one({
        "username": "testuser",
        "password": generate_password_hash("password")
    })
    response = flask_client.post(
        "/login",
        data={"username": "testuser", "password": "password"},
        follow_redirects=True
    )
    assert response.status_code == 200
    # Check if redirected to home page
    assert b'Add Post' in response.data or b'Home' in response.data

def test_logout(flask_client, mock_db):
    """
    Test user logout.
    """
    mock_db.users.insert_one({"username": "testuser", "password": generate_password_hash("password")})
    flask_client.post("/login", data={"username": "testuser", "password": "password"}, follow_redirects=True)

    response = flask_client.get("/logout", follow_redirects=True)
    assert b"login" in response.data

def test_home_logged_out(flask_client, mock_db):
    """
    Access /home logged out should redirect to login.
    """
    response = flask_client.get("/home", follow_redirects=True)
    assert b"login" in response.data

def test_home_logged_in(flask_client, mock_db):
    """
    Access /home logged in should display posts.
    """
    # Insert user and a post
    user_id = mock_db.users.insert_one({"username": "testuser", "password": "hashed"}).inserted_id
    mock_db.posts.insert_one({
        "user": "testuser",
        "title": "A Pet Post",
        "image_id": ObjectId(),
        "created_at": datetime.utcnow()
    })

    login(flask_client, "testuser", user_id)
    response = flask_client.get("/home")
    assert b"home" in response.data

def test_add_post_get(flask_client, mock_db):
    """
    Test GET /addpost when logged in.
    """
    mock_db.users.insert_one({"username": "testuser", "password": "hashed"})
    login(flask_client, "testuser")
    response = flask_client.get("/addpost")
    assert b"addpost" in response.data