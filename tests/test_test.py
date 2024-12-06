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


