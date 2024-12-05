import pytest
from flask import Flask
from pymongo import MongoClient
import bcrypt
from app import app, users_collection


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data


def test_registration_existing_user(client):
    users_collection.insert_one(
        {
            "username": "existinguser",
            "password": bcrypt.hashpw(b"password", bcrypt.gensalt()),
        }
    )
    response = client.post(
        "/register",
        data={"username": "existinguser", "password": "newpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Username already exists" in response.data

    users_collection.delete_one({"username": "existinguser"})


def test_login_failure(client):
    response = client.post(
        "/login",
        data={"username": "nonexistentuser", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid username or password. Please try again." in response.data


def test_profile_access_without_login(client):
    response = client.get("/profile", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page" in response.data


def test_profile_access_with_login(client):
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"Your Profile" in response.data


def test_logout(client):
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data


def test_profile_without_login(client):
    response = client.get("/profile", follow_redirects=True)
    assert response.status_code == 200
    assert b"Please log in to access this page" in response.data


def test_search_recipes_empty_pantry(client):
    with client.session_transaction() as sess:
        sess["username"] = "testuser"
    response = client.get("/search", follow_redirects=True)

    assert response.status_code == 200

    with client.session_transaction() as sess:
        flashes = sess["_flashes"]
        assert any("Your pantry is empty" in msg for category, msg in flashes)
