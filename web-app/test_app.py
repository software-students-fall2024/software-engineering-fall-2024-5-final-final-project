"""
Unit tests for the app's main functionality.
"""

import json
from unittest.mock import patch


# Test the index route
def test_index(test_client):
    """Test if the index route returns status code 200 and contains expected content."""
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"AI Sentence Checker" in response.data


# Test the /checkSentiment route
@patch("app.collection.insert_one")
def test_submit_sentence(mock_insert, test_client):
    """Test if the /checkSentiment route handles valid input correctly."""
    # Mock the insertion to prevent actual MongoDB interaction
    mock_insert.return_value.inserted_id = "fake_id"

    data = {"sentence": "This is a test paragraph. It contains multiple sentences."}
    response = test_client.post(
        "/checkSentiment", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 200
    response_data = response.get_json()
    assert "request_id" in response_data
    assert isinstance(response_data["request_id"], str)


# Test the /checkSentiment route with an empty input
@patch("app.collection.insert_one")
def test_submit_sentence_empty(mock_insert, test_client):
    """Test if the /checkSentiment route handles empty input correctly."""
    _ = mock_insert  # Prevent linting error for unused mock_insert argument

    data = {"sentence": ""}
    response = test_client.post(
        "/checkSentiment", data=json.dumps(data), content_type="application/json"
    )

    assert response.status_code == 200
    response_data = response.get_json()
    assert "request_id" in response_data
    assert isinstance(response_data["request_id"], str)


# Test the /get_analysis route
@patch("app.collection.find_one")
def test_get_analysis(mock_find, test_client):
    """Test if the /get_analysis route returns the expected analysis for a given request_id."""
    # Mock the document retrieval
    mock_find.return_value = {
        "_id": "fake_id",
        "request_id": "unique_request_id",
        "sentences": [
            {
                "sentence": "This is a test.",
                "status": "processed",
                "analysis": {"compound": 0.5},
            }
        ],
        "overall_status": "processed",
        "timestamp": "2024-11-16T04:20:00",
    }

    response = test_client.get("/get_analysis?request_id=unique_request_id")

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["request_id"] == "unique_request_id"
    assert response_data["overall_status"] == "processed"


# Test the /get_analysis route for a missing request_id
@patch("app.collection.find_one")
def test_get_analysis_not_found(mock_find, test_client):
    """Test if the /get_analysis route returns 404 when the request_id is not found."""
    # Mock the document not being found
    mock_find.return_value = None

    response = test_client.get("/get_analysis?request_id=missing_request_id")

    assert response.status_code == 404
    response_data = response.get_json()
    assert response_data["message"] == "No processed analysis found"
