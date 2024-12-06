import pytest
import os
from backend import create_app


@pytest.fixture
def client():
    """Create the test client for Flask app using mongomock."""
    os.environ['MONGO_URI'] = 'mongomock://localhost'
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client


def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200
