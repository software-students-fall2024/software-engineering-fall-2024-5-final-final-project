import pytest
from unittest.mock import MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock mongo
import mongomock
import pymongo

pymongo.MongoClient = mongomock.MongoClient

from backend import create_app


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    test_app = create_app()
    test_app.config.update(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
        }
    )
    yield test_app


@pytest.fixture
def client(app):
    """Create the test client."""
    return app.test_client()
