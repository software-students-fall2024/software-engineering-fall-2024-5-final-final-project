import pytest
from app import create_app



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
        """Provide a simple CNN model instance."""
        return CNNModel()
        
    # write more tests here...