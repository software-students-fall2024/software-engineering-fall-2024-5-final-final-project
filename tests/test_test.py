import pytest
from app import app
import pymongo


def test_secret():
    assert app.config["SECRET_KEY"] is not None


@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_collections(monkeypatch):
    class MockMongoClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_database(self, *args, **kwargs):
            return self

        def get_collection(self, *args, **kwargs):
            return self

        def insert_one(self, document):
            return True

    monkeypatch.setattr(pymongo, "MongoClient", MockMongoClient)


def test_register_user_success(test_client, mock_collections):
    """
    Test successful user registration.
    """
    response = test_client.post(
        "/register",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Registration successful" in response.data
