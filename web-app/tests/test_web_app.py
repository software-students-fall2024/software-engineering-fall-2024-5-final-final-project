# tests/conftest.py
import sys
import os
import pytest
from flask import session
from pymongo import MongoClient
from bson.objectid import ObjectId
import bcrypt

# Add the project root directory to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Now import your app
from app import app, users_collection, bars_collection


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test_secret_key"

    with app.test_client() as client:
        with app.app_context():
            yield client


@pytest.fixture
def logged_in_user(client):
    # Create a test user
    username = "testuser"
    password = "testpassword"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    # Insert test user into database
    user = {"username": username, "password": hashed_password}
    result = users_collection.insert_one(user)
    user_id = str(result.inserted_id)

    # Login the user
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["username"] = username

    yield {"user_id": user_id, "username": username, "password": password}

    # Cleanup: remove test user after test
    users_collection.delete_one({"_id": ObjectId(user_id)})
    bars_collection.delete_many({"user_id": user_id})


# tests/test_routes.py
def test_account_route(client):
    response = client.get("/account")
    assert response.status_code == 200


def test_login_route_get(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_signup_route_get(client):
    response = client.get("/signup")
    assert response.status_code == 200


def test_login_route_post_success(client):
    # Create a test user
    username = "logintest"
    password = "loginpassword"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users_collection.insert_one({"username": username, "password": hashed_password})

    # Attempt login
    response = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Cleanup
    users_collection.delete_one({"username": username})


def test_login_route_post_failure(client):
    response = client.post(
        "/login",
        data={"username": "nonexistent", "password": "wrongpassword"},
        follow_redirects=True,
    )

    # More flexible assertion
    assert response.status_code == 200
    assert b"login" in response.data.lower()


def test_signup_route_post_new_user(client):
    response = client.post(
        "/signup",
        data={"username": "newuser", "password": "newpassword"},
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Verify user was created
    user = users_collection.find_one({"username": "newuser"})
    assert user is not None

    # Cleanup
    users_collection.delete_one({"username": "newuser"})


def test_index_route_unauthenticated(client):
    response = client.get("/", follow_redirects=True)
    assert response.status_code == 200

    # More flexible assertion
    assert b"login" in response.data.lower() or b"signup" in response.data.lower()


def test_index_route_authenticated(logged_in_user, client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_route_get(logged_in_user, client):
    response = client.get("/add")
    assert response.status_code == 200


def test_add_route_post(logged_in_user, client):
    response = client.post(
        "/add",
        data={
            "name": "Test Bar",
            "type": "Cocktail",
            "occasion": "Casual",
            "area": "Downtown",
            "reservation": "No",
            "cost": "$$$",
            "status": "Not Visited",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    # Verify bar was added
    bar = bars_collection.find_one(
        {"name": "Test Bar", "user_id": logged_in_user["user_id"]}
    )
    assert bar is not None


def test_edit_route_get(logged_in_user, client):
    # First add a bar to edit
    bar_data = {
        "user_id": logged_in_user["user_id"],
        "name": "Bar to Edit",
        "type": "Pub",
        "occasion": "Casual",
        "area": "Midtown",
        "reservation": "No",
        "cost": "$$",
        "status": "Not Visited",
    }
    result = bars_collection.insert_one(bar_data)
    bar_id = str(result.inserted_id)

    response = client.get(f"/edit/{bar_id}")
    assert response.status_code == 200

    # Edit the bar
    edit_response = client.post(
        f"/edit/{bar_id}",
        data={
            "name": "Edited Bar Name",
            "type": "Pub",
            "occasion": "Casual",
            "area": "Midtown",
            "reservation": "No",
            "cost": "$$",
            "status": "Not Visited",
        },
        follow_redirects=True,
    )

    assert edit_response.status_code == 200

    # Verify bar was updated
    updated_bar = bars_collection.find_one({"_id": ObjectId(bar_id)})
    assert updated_bar["name"] == "Edited Bar Name"


def test_delete_route(logged_in_user, client):
    # First add a bar to delete
    bar_data = {
        "user_id": logged_in_user["user_id"],
        "name": "Bar to Delete",
        "type": "Cocktail",
        "occasion": "Casual",
        "area": "Downtown",
        "reservation": "No",
        "cost": "$$$",
        "status": "Not Visited",
    }
    result = bars_collection.insert_one(bar_data)
    bar_id = str(result.inserted_id)

    # Get delete confirmation page
    get_response = client.get(f"/delete/{bar_id}")
    assert get_response.status_code == 200

    # Post to delete the bar
    delete_response = client.post(f"/delete/{bar_id}", follow_redirects=True)
    assert delete_response.status_code == 200

    # Verify bar was deleted
    deleted_bar = bars_collection.find_one({"_id": ObjectId(bar_id)})
    assert deleted_bar is None


def test_sort_route(logged_in_user, client):
    # Add some test bars
    bars_collection.insert_many(
        [
            {
                "user_id": logged_in_user["user_id"],
                "name": "Bar One",
                "type": "Cocktail",
                "cost": "$$",
            },
            {
                "user_id": logged_in_user["user_id"],
                "name": "Bar Two",
                "type": "Pub",
                "cost": "$$$",
            },
        ]
    )

    # Test sort by Cost ascending
    response = client.post("/sort", data={"category": "cost", "order": "asc"})
    assert response.status_code == 200
    assert b"Bar One" in response.data
    assert b"Bar Two" in response.data


def test_logout_route(logged_in_user, client):
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    # Check if session is cleared
    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "username" not in sess


# Add more tests as needed...


# Recommendations route test (simplified)
def test_recommendations_route(logged_in_user, client, monkeypatch):
    def mock_recommend_bars(user_bar_names, bars_df, cosine_sim):
        return [
            {
                "name": "Recommended Bar 1",
                "type": "Cocktail",
                "occasion": "Casual",
                "area": "Downtown",
                "reservation": "Yes",
                "cost": "$$",
            }
        ]

    # Monkeypatch the recommend_bars function
    monkeypatch.setattr("app.recommend_bars", mock_recommend_bars)

    response = client.get("/recs")
    assert response.status_code == 200
    assert b"Recommended Bar 1" in response.data


# requirements.txt for tests
"""
pytest
pytest-flask
pymongo
bcrypt
pandas
flask
python-dotenv
"""
