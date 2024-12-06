"""
Unit testing for the web application
"""

import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client