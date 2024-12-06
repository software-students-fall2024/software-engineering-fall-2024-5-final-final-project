import pytest
from backend import create_app


@pytest.fixture
def client():
    """Create the test client for Flask app with mocked Database."""
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client


def test_index(client):
    """Test the index route."""
    response = client.get("/")
    assert response.status_code == 200
