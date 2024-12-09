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

    mock_users = mock_db.users
    mock_posts = mock_db.posts

    fs_mock = MagicMock()
    fs_mock.put.return_value = ObjectId()
    fs_mock.get.return_value.read.return_value = b"image_data"
    fs_mock.get.return_value.content_type = "image/png"

    monkeypatch.setattr("app.db", mock_db)
    monkeypatch.setattr("app.users_collection", mock_users)
    monkeypatch.setattr("app.posts_collection", mock_posts)
    monkeypatch.setattr("app.fs", fs_mock)

    return mock_db

@pytest.fixture
def mock_gridfs(monkeypatch):
    """
    Mock the GridFS object using MagicMock.
    """
    fs_mock = MagicMock()
    fs_mock.put.return_value = ObjectId()
    fs_mock.get.return_value.read.return_value = b"image_data"
    fs_mock.get.return_value.content_type = "image/png"
    monkeypatch.setattr("app.fs", fs_mock)
    return fs_mock

def login(flask_client, username="testuser", user_id=None):
    with flask_client.session_transaction() as sess:
        sess['user_id'] = str(user_id if user_id else ObjectId())
        
def register_and_login(flask_client, username="testuser", password="password"):
    """
    Helper function to register and log in a user.
    """
    response = flask_client.post(
        "/register",
        data={"username": username, "password1": password, "password2": password},
        follow_redirects=True
    )
    assert response.status_code == 200
    response = flask_client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b"Home" in response.data or b"Add Post" in response.data
    return response

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

def test_add_post_post(flask_client, mock_db, mock_gridfs):
    """
    Test POST /addpost to create a new post.
    """
    register_and_login(flask_client, username="testuser", password="password")

    data = {
        "title": "My Pet Post",
        "content": "Cute pet content",
        "image": (BytesIO(b"dummy_image_data"), "pet.png")
    }

    response = flask_client.post(
        "/addpost",
        data=data,
        content_type='multipart/form-data',
        follow_redirects=True
    )

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    assert b"Post created successfully!" in response.data or b"My Pet Post" in response.data, "Success message or post title not found in response."

    post = mock_db.posts.find_one({"title": "My Pet Post"})
    assert post is not None, "Post was not created in the database."

    assert post["title"] == "My Pet Post", "Post title does not match."
    assert post["content"] == "Cute pet content", "Post content does not match."
    assert "image_id" in post and isinstance(post["image_id"], ObjectId), "Post does not have a valid 'image_id'."
    assert post["likes"] == 0, "Initial likes should be 0."
    assert "liked_by" in post and isinstance(post["liked_by"], list), "'liked_by' should be a list."

    mock_gridfs.put.assert_called_once_with(b"dummy_image_data", filename="pet.png", content_type="image/png")



def test_like_post(flask_client, mock_db, mock_gridfs):
    """
    Test liking a post.
    """
    register_and_login(flask_client, username="testuser", password="password")

    post_id = mock_db.posts.insert_one({
        "user": "testuser",
        "title": "Likeable Post",
        "image_id": ObjectId(),
        "likes": 0,
        "liked_by": []
    }).inserted_id

    response = flask_client.post(f"/like_post/{post_id}", follow_redirects=True)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    updated_post = mock_db.posts.find_one({"_id": post_id})
    assert updated_post is not None, "Post should exist in the database."
    assert updated_post["likes"] == 1, f"Expected likes to be 1, got {updated_post['likes']}"
    assert "testuser" in updated_post["liked_by"], "'testuser' should be in 'liked_by' list."


def test_follow_user(flask_client, mock_db):
    """
    Test following another user.
    """
    register_and_login(flask_client, username="testuser", password="password")

    mock_db.users.insert_one({"username": "targetuser", "followers": [], "following": [], "password": "hashed"})

    response = flask_client.post("/follow/targetuser", follow_redirects=True)
    
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None, "Response should contain JSON data."

    assert data["action"] == "followed"

    assert data["followers_count"] == 1

    target_user = mock_db.users.find_one({"username": "targetuser"})
    assert target_user is not None, "Target user should exist in the database."

    assert "testuser" in target_user["followers"]


def test_user_profile(flask_client, mock_db, mock_gridfs):
    """
    Test viewing a user's profile.
    """
    register_and_login(flask_client, username="testuser", password="password")

    mock_db.users.insert_one({
        "username": "profileuser",
        "followers": [],
        "following": [],
        "password": "hashed"
    })

    post_id = mock_db.posts.insert_one({
        "user": "profileuser",
        "title": "Profile Post",
        "content": "This is the content of the profile post.", 
        "image_id": ObjectId(),
        "created_at": datetime.utcnow(),
        "likes": 0,
        "liked_by": []
    }).inserted_id

    response = flask_client.get("/profile/profileuser", follow_redirects=True)

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    assert b"Profile Post" in response.data, "Profile Post title not found in the response."


def test_add_comment(flask_client, mock_db, mock_gridfs):
    """
    Test adding a comment to a post.
    """
    register_and_login(flask_client, username="testuser", password="password")

    post_id = mock_db.posts.insert_one({
        "user": "testuser",
        "title": "Commentable Post",
        "content": "This is a commentable post.", 
        "image_id": ObjectId(),
        "comments": []
    }).inserted_id

    response = flask_client.post(
        f"/posts/{post_id}/comments",
        data={"content": "Nice post!"},
        follow_redirects=True
    )

    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}"

    updated_post = mock_db.posts.find_one({"_id": post_id})
    assert updated_post is not None, "Post should exist in the database."
    assert len(updated_post["comments"]) == 1, "Expected one comment after adding."
    assert updated_post["comments"][0]["content"] == "Nice post!", "Comment content does not match."



def test_edit_profile(flask_client, mock_db, mock_gridfs):
    """
    Test editing the username.
    """
    register_and_login(flask_client, username="oldname", password="password")
    
    post_id = mock_db.posts.insert_one({
        "user": "oldname",
        "title": "Old Name Post",
        "content": "This is a post by oldname.",  
        "image_id": ObjectId(),
        "created_at": datetime.utcnow(),
        "likes": 0,
        "liked_by": []
    }).inserted_id

    response = flask_client.post(
        "/edit-username",
        data={"new_username": "newname"},
        follow_redirects=True
    )

    updated_user = mock_db.users.find_one({"_id": post_id})  
    updated_user = mock_db.users.find_one({"username": "newname"})
    assert updated_user is not None, "Updated user not found in the database."
    assert updated_user["username"] == "newname", "Username was not updated correctly."

    updated_post = mock_db.posts.find_one({"_id": post_id})
    assert updated_post is not None, "Post not found in the database."
    assert updated_post["user"] == "newname", "Post's 'user' field was not updated to the new username."
