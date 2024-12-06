import pytest
from app import app


def test_secret():
    assert app.config["SECRET_KEY"] is not None


@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_mock_db(monkeypatch, test_client):
    class MockMongoClient:
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            return self

    monkeypatch.setattr("pymongo.MongoClient", MockMongoClient)

    response = test_client.get("/")
    assert response.status_code == 200
