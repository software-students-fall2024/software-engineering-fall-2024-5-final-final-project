import pytest
from backend import create_app


@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    """Create the test client."""
    return app.test_client()
