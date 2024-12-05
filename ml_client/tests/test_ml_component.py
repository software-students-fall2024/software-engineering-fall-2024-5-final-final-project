"""
Tests for ml-client flask app
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

    def model(self):
        """Provide a simple model instance."""
        return True

    # write more tests here...
