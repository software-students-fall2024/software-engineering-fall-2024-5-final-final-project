import pytest

# from backend import create_app




def test_dummy():
    """ fake test for now"""
    assert True


# @pytest.mark.skip(
#     reason="Temporarily disabling tests due to database connection issues"
# )
# def client():
#     """Create the test client"""
#     app = create_app()
#     app.testing = True
#     with app.test_client() as client:
#         yield client


# @pytest.mark.skip(
#     reason="Temporarily disabling tests due to database connection issues"
# )
# def test_index(client):
#     """Test the index route."""
#     response = client.get("/")
#     assert response.status_code == 200
