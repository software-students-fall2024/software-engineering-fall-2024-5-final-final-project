import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend import create_app


@pytest.fixture(scope="session")
def app():
    """Create application for the tests."""
    test_app = create_app()
    test_app.config.update(
        {
            "TESTING": True,
        }
    )
    yield test_app


@pytest.fixture
def client(app):
    """Create the test client."""
    return app.test_client()
