"""
Tests for web-app flask app
"""
import pytest
from app import create_app


@pytest.fixture
def app():
    """Fixture for creating and configuring the Flask app."""
    test_app = create_app()
    return test_app


class Tests:
    """Test functions"""

    def test_sanity_check(self):
        """
        Test debugging... making sure that we can run a simple test that always passes.
        """
        expected = True
        actual = True
        assert actual == expected, "Expected True to be equal to True!"

    def test_home_page(self, test_app):
        """Test the home page route."""
        with test_app.test_client() as client:
            assert client.get("/").status_code == 200

    # write more tests here...
