"""
Unit testing for the web application
"""

import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_home(client):
    """Test GET /"""

    response = client.get("/")
    html = response.data.decode("utf-8")

    assert response.status_code == 200