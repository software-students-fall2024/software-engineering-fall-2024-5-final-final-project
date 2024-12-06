import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(scope="session", autouse=True)
def mock_database():
    """Mock the Database class for all tests."""
    with patch("backend.routes.Database") as MockDatabase:
        mock_db = MagicMock()

        # Mock db
        mock_db.get_user_data.return_value = {
            "username": "user",
            "budget": 1000.0,
            "total_expenses": 200.0,
        }

        mock_db.get_expenses.return_value = []

        MockDatabase.return_value = mock_db

        yield
