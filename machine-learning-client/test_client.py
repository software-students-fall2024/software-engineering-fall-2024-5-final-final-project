"""Test module for Machine learning client"""

# test_client.py
# cd machine-learning-client
# pytest test_client.py -v
# pytest -v

# pylint web-app/ machine-learning-client/
# black .



import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
import mongomock

# Fixture to mock MongoClient before importing client.py
@pytest.fixture
def mock_mongo(monkeypatch):
    mock_client = mongomock.MongoClient()
    # Patch 'MongoClient' in the 'client' module before it's imported
    monkeypatch.setattr("client.MongoClient", lambda uri: mock_client)
    return mock_client

# Fixture to import the app after MongoClient is mocked
@pytest.fixture
def client(mock_mongo):
    from client import app  # Import after mocking
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Fixture to mock the 'infer' method of the Roboflow Inference Client
@pytest.fixture
def mock_rf_infer():
    with patch("client.rf_client.infer") as mock:
        yield mock

# Test the /predict route successfully
def test_predict_success(client, mock_rf_infer, mock_mongo):
    mock_rf_infer.return_value = {
        "predictions": [{"class": "rock", "confidence": 0.95}]
    }

    data = {
        "image": (BytesIO(b"fake image data"), "test_image.jpg")
    }

    response = client.post("/predict", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "rock"
    assert json_data["confidence"] == 0.95

    # Verify that the prediction was stored in MongoDB
    mock_db = mock_mongo["rps_database"]["predictions"]
    prediction = mock_db.find_one({"gesture": "rock"})
    assert prediction is not None
    assert prediction["prediction_score"] == 0.95
    assert prediction["image_metadata"]["filename"] == "test_image.jpg"

# Test the /predict route with no image provided
def test_predict_no_image(client):
    response = client.post("/predict", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "No image file provided"

# Test the /predict route with inference failure
def test_predict_inference_failure(client, mock_rf_infer):
    mock_rf_infer.side_effect = Exception("Inference API error")

    data = {
        "image": (BytesIO(b"fake image data"), "test_image.jpg")
    }

    response = client.post("/predict", data=data, content_type="multipart/form-data")
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Prediction error" in json_data["error"]
    assert "Inference API error" in json_data["error"]

# Test the /predict route with MongoDB insertion failure
def test_predict_mongodb_failure(client, mock_rf_infer):
    mock_rf_infer.return_value = {
        "predictions": [{"class": "paper", "confidence": 0.85}]
    }

    with patch("client.collection.insert_one", side_effect=Exception("MongoDB insertion error")):
        data = {
            "image": (BytesIO(b"fake image data"), "test_image.jpg")
        }

        response = client.post("/predict", data=data, content_type="multipart/form-data")
        assert response.status_code == 500
        json_data = response.get_json()
        assert "Prediction error" in json_data["error"]
        assert "MongoDB insertion error" in json_data["error"]

# Test the /predict route with invalid inference response (missing 'class' key)
def test_predict_invalid_inference_response(client, mock_rf_infer, mock_mongo):
    mock_rf_infer.return_value = {"predictions": [{"confidence": 0.80}]}  # Missing 'class'

    data = {
        "image": (BytesIO(b"fake image data"), "test_image.jpg")
    }

    response = client.post("/predict", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "Unknown"
    assert json_data["confidence"] == 0

# Test the /predict route with FileNotFoundError during file saving
def test_predict_file_not_found(client, mock_rf_infer, mock_mongo):
    with patch("werkzeug.datastructures.FileStorage.save", side_effect=FileNotFoundError("File not found")):
        data = {
            "image": (BytesIO(b"fake image data"), "test_image.jpg")
        }

        response = client.post("/predict", data=data, content_type="multipart/form-data")
        assert response.status_code == 500
        json_data = response.get_json()
        assert "Prediction error" in json_data["error"]
        assert "File not found" in json_data["error"]

