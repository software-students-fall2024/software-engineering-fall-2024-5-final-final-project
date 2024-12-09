"""Tests for the web app"""

# pylint: disable=redefined-outer-name
import sys
import os
from unittest.mock import patch, MagicMock
from bson import ObjectId
import pytest
from werkzeug.security import generate_password_hash


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
from app import create_app


@pytest.fixture
def mock_db():
    """Mock the database."""
    mock_client = MagicMock()
    mock_db_instance = MagicMock()
    mock_client.__getitem__.return_value = mock_db_instance
    
    return mock_db_instance


@pytest.fixture
def client(mock_db):
    """Create a test client."""
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test_secret_key",
        "MONGO_URI": "mongodb://localhost:27017",
        "MONGO_DBNAME": "test_flaskapp",
    }

    mock_client = MagicMock()
    mock_client.admin.command.return_value = {"ok": 1}
    mock_client.__getitem__.return_value = mock_db

    with patch("pymongo.MongoClient", return_value=mock_client):
        app = create_app(test_config)
        with app.test_client() as client:
            yield client


def test_homepage(client, mock_db):
    """Test homepage route status and content."""
    valid_user_id = str(ObjectId())
    mock_wishes = [{"name": "Test Wish", "price": "100"}]

    mock_find = MagicMock()
    mock_sort = MagicMock()
    mock_find.sort.return_value = mock_wishes
    mock_db.wishes.find.return_value = mock_find

    with client.session_transaction() as session:
        session["_user_id"] = valid_user_id

    response = client.get("/")
    assert response.status_code == 200
    assert b"Test Wish" in response.data

def test_login(client, mock_db):
    """Test the login route."""
    valid_user_id = str(ObjectId())
    mock_user_password = "testpassword"
    valid_password_hash = generate_password_hash(mock_user_password)

    mock_user_data = {
        "_id": valid_user_id,
        "username": "testuser",
        "password": valid_password_hash,
        "first-name": "test"
    }

    mock_db.users.find_one.return_value = mock_user_data

    response = client.post("/login", data={
        "username": "testuser",
        "password": mock_user_password,
    }, follow_redirects=True)

    assert response.status_code == 200

    with client.session_transaction() as session:
        flashed_messages = session.get("_flashes", [])
        assert ("message", "Log in success!") in flashed_messages

def test_add_item(client, mock_db):
    """Test adding an item to the wishlist."""
    valid_user_id = str(ObjectId())
    with client.session_transaction() as session:
        session["_user_id"] = valid_user_id

    mock_db.wishes.insert_one.return_value = True

    response = client.post("/add", data={
        "item_image": "http://example.com/image.jpg",
        "item_name": "Test Item",
        "item_price": "50",
        "item_link": "http://example.com/item",
        "item_comments": "Test comment"
    }, follow_redirects=True)

    assert response.status_code == 200

    with client.session_transaction() as session:
        flashed_messages = session.get("_flashes", [])
        assert ("message", "Item added!") in flashed_messages

def test_edit_item(client, mock_db):
    """Test editing an item in the wishlist."""
    valid_user_id = str(ObjectId())
    valid_item_id = str(ObjectId())

    mock_db.wishes.find_one.return_value = {
        "_id": valid_item_id,
        "user_id": valid_user_id,
        "name": "Old Item",
        "price": "30"
    }

    mock_db.wishes.update_one.return_value.modified_count = 1

    with client.session_transaction() as session:
        session["_user_id"] = valid_user_id

    response = client.post(f"/edit/{valid_item_id}", data={
        "item_image": "http://example.com/new_image.jpg",
        "item_name": "Updated Item",
        "item_price": "40",
        "item_link": "http://example.com/new_item"
    }, follow_redirects=True)

    assert response.status_code == 200

    with client.session_transaction() as session:
        flashed_messages = session.get("_flashes", [])
        assert ("message", "Wish updated successfully!") in flashed_messages

def test_delete_item(client, mock_db):
    """Test deleting an item from the wishlist."""
    valid_user_id = str(ObjectId())
    valid_item_id = str(ObjectId())

    mock_db.wishes.delete_one.return_value.deleted_count = 1

    with client.session_transaction() as session:
        session["_user_id"] = valid_user_id

    response = client.post(f"/delete/{valid_item_id}", follow_redirects=True)

    assert response.status_code == 200

    with client.session_transaction() as session:
        flashed_messages = session.get("_flashes", [])
        assert ("message", "Wish deleted successfully!") in flashed_messages

def test_view_claimed_gifts(client, mock_db):
    """Test viewing claimed gifts."""
    valid_user_id = str(ObjectId())
    mock_user = {
        "_id": ObjectId(valid_user_id), 
        "username": "testuser",
        "first-name": "Test",
        "last-name": "User"
    }
    mock_claimed_wishes = [
        {"name": "Claimed Wish 1", "price": "150"},
        {"name": "Claimed Wish 2", "price": "250"},
    ]

    # Mock database responses
    mock_db.users.find_one.return_value = mock_user
    mock_db.wishes.find.return_value.sort.return_value = mock_claimed_wishes

    # Simulate a logged-in session
    with client.session_transaction() as session:
        session["_user_id"] = valid_user_id

    # Test the claimed gifts route
    response = client.get(f"/claimed/{mock_user['username']}")
    assert response.status_code == 200
    assert b"Claimed Wish 1" in response.data
    assert b"Claimed Wish 2" in response.data

def test_claim_gift(client, mock_db):
    """Test claiming a gift."""
    valid_user_id = str(ObjectId())
    valid_wish_id = str(ObjectId())

    mock_db.wishes.find_one.return_value = {
        "_id": valid_wish_id,
        "name": "Test Wish",
        "price": "100",
        "claimed_by": None,
    }

    mock_db.wishes.update_one.return_value.modified_count = 1

    with client.session_transaction() as session:
        session["_user_id"] = valid_user_id

    response = client.post(f"/claim/{valid_wish_id}", follow_redirects=True)

    assert response.status_code == 200

    with client.session_transaction() as session:
        flashed_messages = session.get("_flashes", [])
        assert ("message", "Gift claimed successfully!") in flashed_messages

def test_view_wishlist(client, mock_db):
    """Test viewing a user's wishlist."""
    valid_user_id = str(ObjectId())
    mock_user = {"_id": valid_user_id, "username": "testuser"}
    mock_wishes = [
        {"name": "Wish 1", "price": "100"},
        {"name": "Wish 2", "price": "200"},
    ]

    mock_db.users.find_one.return_value = mock_user
    mock_db.wishes.find.return_value.sort.return_value = mock_wishes

    response = client.get(f"/wishlist/{mock_user['username']}")
    assert response.status_code == 200
    assert b"Wish 1" in response.data
    assert b"Wish 2" in response.data
