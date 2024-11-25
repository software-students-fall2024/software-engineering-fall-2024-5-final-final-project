"""
Testing code for web app frontend
"""

import pytest


class Tests:
    """Test functions"""

    def test_sanity_check(self):
        """
        Test debugging, make test that always passes
        """
        expected = True
        actual = True
        assert actual == expected, "Expected True to be equal to True!"
