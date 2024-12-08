"""
Tests for web-app flask app
"""
import pytest
import requests
from flask import Flask
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def test_app():
    """Fixture for creating and configuring the Flask app."""
    test_app = create_app()
    return test_app


@pytest.fixture
def client(test_app):
    """Fixture to create a test client for the app."""
    return test_app.test_client()


class Tests:
    """Test functions"""

    def test_sanity_check(self):
        """
        Test debugging... making sure that we can run a simple test that always passes.
        """
        expected = True
        actual = True
        assert actual == expected, "Expected True to be equal to True!"

    def test_home_page(self, client):
        """Test the home page route."""
        assert client.get("/").status_code == 200

    def test_instantiation(self, test_app):
        """Test if the app instance is correctly created."""
        assert isinstance(test_app, Flask), "Expected test_app to be an instance of Flask!"


    @patch("app.requests.post")
    def test_call_model_success(self, mock_post, client):
        """
        Test /call_model route when the ML client responds successfully.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Mocked ML Response"}
        mock_post.return_value = mock_response

        response = client.post(
            "/call_model",
            data={"user_input": "Test input"},
        )

        assert response.status_code == 200
        assert response.json == {"response": "Mocked ML Response"}


    @patch("app.requests.post")
    def test_call_model_failure(self, mock_post, client):
        """
        Test /call_model route when the ML client returns an error.
        """
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Mocked error from ML client"
        mock_post.return_value = mock_response

        response = client.post(
            "/call_model",
            data={"user_input": "Test input"},
        )

        assert response.status_code == 500
        assert "Failed to call /respond" in response.get_json()["response"]


    @patch("app.requests.post")
    def test_call_model_connection_error(self, mock_post, client):
        """
        Test /call_model route when there is a connection error to the ML client.
        """

        mock_post.side_effect = requests.exceptions.ConnectionError

        response = client.post(
            "/call_model",
            data={"user_input": "Test input"},
        )

        assert response.status_code == 500
        assert response.json["response"] == "Error connecting to ml-client"



    @patch("app.requests.post")
    def test_call_model_unexpected_error(self, mock_post, client):
        """
        Test /call_model route when an unexpected error occurs.
        """
        mock_post.side_effect = Exception("Unexpected error")

        response = client.post(
            "/call_model",
            data={"user_input": "Test input"},
        )

        assert response.status_code == 500
        assert "Unexpected error" in response.get_json()["response"]

   # write more tests here...
