"""
Testing code for web app frontend
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch
from flask import url_for

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app as flask_app
from user.user import User


@pytest.fixture
def mock_db(monkeypatch):
    """Mock MongoDB."""
    mock_db = MagicMock()
    mock_users = mock_db.users
    mock_users.find_one.side_effect = lambda query: (
        {
            "email": "testuser@example.com",
            "password": "hashedpassword",
            "firstname": "Test",
            "lastname": "User",
            "events": [
                {
                    "Amount": 50.75,
                    "Category": "Food",
                    "Date": "2024-12-06",
                    "Memo": "Dinner at a restaurant",
                },
                {
                    "Amount": 50.75,
                    "Category": "Transportation",
                    "Date": "2024-12-06",
                    "Memo": "Train",
                },
            ],
        }
        if query.get("email") == "testuser@example.com"
        else None
    )
    mock_db.users = mock_users
    monkeypatch.setattr("database.db", mock_db)
    return mock_db


@pytest.fixture
def mock_user():
    """Mock a logged-in user."""
    mock_user = MagicMock(spec=User)
    mock_user.email = "testuser@example.com"
    mock_user.firstname = "Test"
    mock_user.lastname = "User"
    mock_user.get_id.return_value = "testuser@example.com"
    mock_user.is_authenticated = True
    mock_user.get_events.return_value = [
        {
            "Amount": 50.75,
            "Category": "Food",
            "Date": "2024-12-06",
            "Memo": "Dinner at a restaurant",
        },
        {
            "Amount": 50.75,
            "Category": "Transportation",
            "Date": "2024-12-06",
            "Memo": "Train",
        },
    ]
    return mock_user


@pytest.fixture
def client(mock_db):
    """Test client for Flask app."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        with flask_app.app_context():
            yield client


class Tests:
    """Test functions"""

    def test_sanity_check(self):
        """Test debugging sanity check."""
        expected = True
        actual = True
        assert actual == expected, "Expected True to be equal to True!"

    @patch("flask_login.utils._get_user")
    def test_user_login(self, mock_get_user, client, mock_db):
        """Test user login."""
        mock_user = MagicMock(spec=User, email="testuser@example.com")
        mock_get_user.return_value = mock_user

        response = client.post(
            "/user/login",
            data={"email": "testuser@example.com", "password": "password123"},
        )
        assert response.status_code == 302  # Redirect after login
        assert response.location.endswith(url_for("index"))

    @patch("flask_login.utils._get_user")
    def test_user_add_event(self, mock_get_user, client, mock_user):
        """Test adding an event for a logged-in user."""
        mock_get_user.return_value = mock_user

        response = client.post(
            "/user/add-event",
            json={
                "Amount": 100.0,
                "Category": "Entertainment",
                "Date": "2024-12-07",
                "Memo": "Movie night",
            },
        )
        assert response.status_code == 200
        assert response.json == {"message": "Event added successfully"}
        mock_user.add_event.assert_called_once()

    @patch("flask_login.utils._get_user")
    def test_get_events(self, mock_get_user, client, mock_user):
        """Test retrieving user events."""
        mock_get_user.return_value = mock_user

        response = client.get("/user/get-events")
        assert response.status_code == 200
        events = response.json
        assert len(events) == 2
        assert events[0]["Category"] == "Food"
        assert events[1]["Category"] == "Transportation"

    @patch("flask_login.utils._get_user")
    def test_analytics_data(self, mock_get_user, client, mock_user):
        """Test analytics data."""
        mock_get_user.return_value = mock_user

        response = client.get("/user/analytics-data")
        assert response.status_code == 200
        analytics = response.json
        assert "2024-12" in analytics
        assert analytics["2024-12"]["Food"] == 50.75
