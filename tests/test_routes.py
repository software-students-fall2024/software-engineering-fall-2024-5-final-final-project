import pytest
from unittest.mock import MagicMock, patch
from backend import create_app

#TODO: Fix the test

# @pytest.fixture
# def client():
#     """Create the test client for Flask app with mocked Database."""
#     with patch('backend.routes.Database') as MockDatabase:
#         mock_db = MagicMock()
        
#         # Mock the DB
#         mock_db.get_user_data.return_value = {
#             "username": "user",
#             "budget": 1000.0,
#             "total_expenses": 200.0
#         }
        
#         mock_db.get_expenses.return_value = []
        
#         MockDatabase.return_value = mock_db

#         app = create_app()
#         app.config['TESTING'] = True
#         with app.test_client() as client:
#             yield client


# def test_index(client):
#     """Test the index route."""
#     response = client.get("/")
#     assert response.status_code == 200
