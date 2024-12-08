import pytest
from ml_client import app, analyze
import json


@pytest.fixture
def client():
    """
    Creates a test client for the Flask app.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_analyze_function_valid_input():
    """
    Test the `analyze` function directly with a valid input.
    """
    # Simulate a valid input
    data = {"text": "I am so happy today!"}

    # Call the analyze function
    with app.test_request_context(json=data):
        response = analyze()  # This is always a Flask Response object
    print(response)
    # Extract JSON and status code
    response_body = response.get_json()
    status_code = response.status_code

    # Validate status code
    assert status_code == 200

    # Validate response structure
    assert "top_emotion" in response_body
    assert "all_emotions" in response_body

    # Validate "top_emotion" structure
    top_emotion = response_body["top_emotion"]
    assert "label" in top_emotion
    assert "score" in top_emotion

    # Validate "all_emotions" structure
    all_emotions = response_body["all_emotions"]
    assert isinstance(all_emotions, list)
    for emotion in all_emotions:
        assert "label" in emotion
        assert "score" in emotion


def test_analyze_missing_text(client):
    """
    Test the /analyze endpoint with missing 'text' in the request.
    """
    response = client.post("/analyze", data=json.dumps({}), content_type="application/json")
    
    # Assert the response status code
    assert response.status_code == 400

    # Assert the error message in the response
    assert "error" in response.json
    assert response.json["error"] == "Invalid request"


def test_analyze_valid_request(client):
    """
    Test the /analyze endpoint with a valid 'text' input.
    """
    payload = {"text": "I am so happy today!"}
    response = client.post("/analyze", data=json.dumps(payload), content_type="application/json")
    
    # Assert the response status code
    assert response.status_code == 200

    # Assert the structure of the response
    assert "top_emotion" in response.json
    assert "all_emotions" in response.json

    # Validate the 'top_emotion' structure
    top_emotion = response.json["top_emotion"]
    assert "label" in top_emotion
    assert "score" in top_emotion

    # Validate the 'all_emotions' structure
    all_emotions = response.json["all_emotions"]
    assert isinstance(all_emotions, list)
    for emotion in all_emotions:
        assert "label" in emotion
        assert "score" in emotion

def test_analyze_endpoint_valid_request(client):
    """
    Test the /analyze endpoint with a valid POST request.
    """
    data = {"text": "I am so excited about this project!"}
    response = client.post("/analyze", json=data)

    # Check status code
    assert response.status_code == 200

    # Check response structure
    json_data = response.get_json()
    assert "top_emotion" in json_data
    assert "all_emotions" in json_data


def test_analyze_endpoint_invalid_request(client):
    """
    Test the /analyze endpoint with an invalid POST request (missing 'text').
    """
    data = {}
    response = client.post("/analyze", json=data)

    # Check status code
    assert response.status_code == 400

    # Check error message
    json_data = response.get_json()
    assert "error" in json_data
    assert json_data["error"] == "Invalid request"