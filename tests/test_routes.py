import pytest  # type: ignore
from backend import create_app


@pytest.fixture
def client():
    """Create the test client for Flask app."""
    app = create_app()
    app.testing = True
    with app.test_client() as client:
        yield client


def test_index(self):
    """Test the index route."""
    response = self.get("/")
    assert response.status_code == 200
