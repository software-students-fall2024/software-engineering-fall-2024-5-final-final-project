"""Test module for Machine learning client"""

# test_client.py
# cd machine-learning-client
# pytest test_client.py -v
# pytest -v

# pylint web-app/ machine-learning-client/
# black .


# import pytest
# from unittest.mock import patch, MagicMock
# from io import BytesIO
# import mongomock

# # Fixture to mock MongoClient using mongomock and patch it in the client module
# @pytest.fixture
# def mock_mongo(monkeypatch):
#     """
#     Mock MongoClient using mongomock and patch it in the client module.
#     """
#     mock_client = mongomock.MongoClient()
#     # Patch 'MongoClient' in 'client' module with mongomock's MongoClient
#     monkeypatch.setattr("client.MongoClient", lambda uri: mock_client)
#     return mock_client

# # Fixture to mock rf_client.infer before importing client.py
# @pytest.fixture
# def mock_rf_infer(monkeypatch):
#     """
#     Mock the 'infer' method of the Roboflow Inference Client.
#     """
#     mock_infer = MagicMock()
#     monkeypatch.setattr("client.rf_client.infer", mock_infer)
#     return mock_infer

# # Fixture to mock FileStorage.save
# @pytest.fixture
# def mock_file_save(monkeypatch):
#     """
#     Mock the 'save' method of FileStorage to prevent actual file saving.
#     """
#     mock_save = MagicMock()
#     monkeypatch.setattr("werkzeug.datastructures.FileStorage.save", mock_save)
#     return mock_save

# # Fixture to import the app after mocking and provide the test client
# @pytest.fixture
# def app_client(mock_mongo, mock_rf_infer, mock_file_save):
#     """
#     Import the Flask app after mocking dependencies and provide a test client.
#     """
#     from client import app  # Import after mocks are applied
#     app.config['TESTING'] = True
#     with app.test_client() as client:
#         yield client, mock_mongo, mock_rf_infer, mock_file_save

# # Test the /predict route successfully
# def test_predict_success(app_client):
#     client, mock_mongo_client, mock_infer, mock_save = app_client
#     # Set the return value for rf_client.infer
#     mock_infer.return_value = {
#         "predictions": [{"class": "rock", "confidence": 0.95}]
#     }

#     data = {
#         "image": (BytesIO(b"fake image data"), "test_image.jpg")
#     }

#     response = client.post("/predict", data=data, content_type="multipart/form-data")
#     assert response.status_code == 200
#     json_data = response.get_json()
#     assert json_data["gesture"] == "rock"
#     assert json_data["confidence"] == 0.95

#     # Verify that the prediction was stored in MongoDB
#     mock_db = mock_mongo_client["rps_database"]["predictions"]
#     prediction = mock_db.find_one({"gesture": "rock"})
#     assert prediction is not None
#     assert prediction["prediction_score"] == 0.95
#     assert prediction["image_metadata"]["filename"] == "test_image.jpg"

#     # Verify that file.save was called once
#     mock_save.assert_called_once()

# # Test the /predict route with no image provided
# def test_predict_no_image(app_client):
#     client, _, _, _ = app_client
#     response = client.post("/predict", data={}, content_type="multipart/form-data")
#     assert response.status_code == 400
#     json_data = response.get_json()
#     assert json_data["error"] == "No image file provided"

# # Test the /predict route with inference failure
# def test_predict_inference_failure(app_client):
#     client, _, mock_infer, mock_save = app_client
#     # Set 'rf_client.infer' to raise an exception
#     mock_infer.side_effect = Exception("Inference API error")

#     data = {
#         "image": (BytesIO(b"fake image data"), "test_image.jpg")
#     }

#     response = client.post("/predict", data=data, content_type="multipart/form-data")
#     assert response.status_code == 500
#     json_data = response.get_json()
#     assert "Prediction error" in json_data["error"]
#     assert "Inference API error" in json_data["error"]

#     # Verify that file.save was called once
#     mock_save.assert_called_once()

# # Test the /predict route with MongoDB insertion failure
# def test_predict_mongodb_failure(app_client):
#     client, mock_mongo_client, mock_infer, mock_save = app_client
#     # Set 'rf_client.infer' to return valid data
#     mock_infer.return_value = {
#         "predictions": [{"class": "paper", "confidence": 0.85}]
#     }

#     # Patch 'collection.insert_one' to raise an exception
#     with patch("client.collection.insert_one", side_effect=Exception("MongoDB insertion error")):
#         data = {
#             "image": (BytesIO(b"fake image data"), "test_image.jpg")
#         }

#         response = client.post("/predict", data=data, content_type="multipart/form-data")
#         assert response.status_code == 500
#         json_data = response.get_json()
#         assert "Prediction error" in json_data["error"]
#         assert "MongoDB insertion error" in json_data["error"]

#         # Verify that file.save was called once
#         mock_save.assert_called_once()

# # Test the /predict route with invalid inference response (missing 'class' key)
# def test_predict_invalid_inference_response(app_client):
#     client, mock_mongo_client, mock_infer, mock_save = app_client
#     # Set 'rf_client.infer' to return predictions without 'class'
#     mock_infer.return_value = {"predictions": [{"confidence": 0.80}]}  # Missing 'class'

#     data = {
#         "image": (BytesIO(b"fake image data"), "test_image.jpg")
#     }

#     response = client.post("/predict", data=data, content_type="multipart/form-data")
#     assert response.status_code == 200
#     json_data = response.get_json()
#     assert json_data["gesture"] == "Unknown"
#     assert json_data["confidence"] == 0

#     # Verify that file.save was called once
#     mock_save.assert_called_once()

# # Test the /predict route with FileNotFoundError during file saving
# def test_predict_file_not_found(app_client):
#     client, mock_mongo_client, mock_infer, mock_save = app_client
#     # Configure the mock save to raise FileNotFoundError
#     mock_save.side_effect = FileNotFoundError("File not found")

#     data = {
#         "image": (BytesIO(b"fake image data"), "test_image.jpg")
#     }

#     response = client.post("/predict", data=data, content_type="multipart/form-data")
#     assert response.status_code == 500
#     json_data = response.get_json()
#     assert "Prediction error" in json_data["error"]
#     assert "File not found" in json_data["error"]

#     # Verify that file.save was called once
#     mock_save.assert_called_once()

"""Test module for Machine learning client"""

import os
from unittest.mock import patch, MagicMock
from io import BytesIO
from requests.exceptions import RequestException
from pymongo.errors import PyMongoError
import pytest
from client import app

@pytest.fixture(name="flask_client")
def flask_client_fixture():
    """
    Provide a Flask test client for testing application routes.
    Yields:
        FlaskClient: A test client for the Flask application.
    """
    app.config["TESTING"] = True
    with app.test_client() as temp_client:
        yield temp_client

@pytest.fixture(name="mock_env_variables")
def mock_env_variables_fixture():
    """
    Mock environment variables for testing.
    """
    with patch.dict(os.environ, {
        "MONGO_URI": "mongodb://test:27017",
        "INFERENCE_SERVER_URL": "http://test:9001",
        "ROBOFLOW_API_KEY": "test_key",
        "ROBOFLOW_MODEL_ID": "test_model"
    }):
        yield

# Test successful prediction
@patch("client.rf_client")
@patch("client.collection")
def test_predict_success(mock_collection, mock_rf_client, flask_client):
    """
    Test successful predictions.
    """
    # Mock the inference result
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Rock", "confidence": 0.95}]
    }
    mock_collection.insert_one.return_value = MagicMock()

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post("/predict", content_type="multipart/form-data", data=data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "Rock"
    assert json_data["confidence"] == 0.95
    mock_rf_client.infer.assert_called_once()
    mock_collection.insert_one.assert_called_once()

# Test prediction with no image
def test_predict_no_image(flask_client):
    """Test predictions with no image provided"""
    response = flask_client.post("/predict", content_type="multipart/form-data", data={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "No image file provided"

# Test inference API failure
@patch("client.rf_client")
def test_predict_inference_failure(mock_rf_client, flask_client):
    """Test prediction with an inference failure"""
    mock_rf_client.infer.side_effect = RequestException("Inference API error")
    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    
    response = flask_client.post("/predict", content_type="multipart/form-data", data=data)
    
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Prediction error" in json_data["error"]

# Test MongoDB insertion failure
@patch("client.rf_client")
@patch("client.collection")
def test_predict_mongodb_failure(mock_collection, mock_rf_client, flask_client):
    """Test prediction with a database failure"""
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Paper", "confidence": 0.85}]
    }
    mock_collection.insert_one.side_effect = PyMongoError("MongoDB insertion error")

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post("/predict", content_type="multipart/form-data", data=data)

    assert response.status_code == 500
    json_data = response.get_json()
    assert "Prediction error" in json_data["error"]

# Test FileNotFoundError during file saving
@patch("client.rf_client")
def test_predict_file_not_found(mock_rf_client, flask_client):
    """Test prediction with a file not found error"""
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Scissors", "confidence": 0.90}]
    }

    with patch("werkzeug.datastructures.FileStorage.save", 
              side_effect=FileNotFoundError("File not found")):
        data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
        response = flask_client.post("/predict", content_type="multipart/form-data", data=data)

        assert response.status_code == 500
        json_data = response.get_json()
        assert "Prediction error" in json_data["error"]

# Test unknown gesture prediction
@patch("client.rf_client")
@patch("client.collection")
def test_predict_unknown_gesture(mock_collection, mock_rf_client, flask_client):
    """Test prediction with unknown gesture"""
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Unknown", "confidence": 0.5}]
    }
    mock_collection.insert_one.return_value = MagicMock()

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post("/predict", content_type="multipart/form-data", data=data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "Unknown"
    assert json_data["confidence"] == 0

# Test missing prediction in response
@patch("client.rf_client")
@patch("client.collection")
def test_predict_missing_prediction(mock_collection, mock_rf_client, flask_client):
    """Test prediction with missing prediction in response"""
    mock_rf_client.infer.return_value = {"predictions": []}
    mock_collection.insert_one.return_value = MagicMock()

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post("/predict", content_type="multipart/form-data", data=data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "Unknown"
    assert json_data["confidence"] == 0

# Test missing confidence in prediction
@patch("client.rf_client")
@patch("client.collection")
def test_predict_missing_confidence(mock_collection, mock_rf_client, flask_client):
    """Test prediction with missing confidence in response"""
    mock_rf_client.infer.return_value = {
        "predictions": [{"class": "Rock"}]
    }
    mock_collection.insert_one.return_value = MagicMock()

    data = {"image": (BytesIO(b"fake image data"), "test_image.jpg")}
    response = flask_client.post("/predict", content_type="multipart/form-data", data=data)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["gesture"] == "Rock"
    assert json_data["confidence"] == 0


