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


import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
from io import BytesIO
from app import app  # Import the Flask app

class TestRPSPredictionService(unittest.TestCase):
    def setUp(self):
        """Set up test client and other test fixtures"""
        self.app = app
        self.client = self.app.test_client()
        
        # Create a mock image file
        self.mock_image = (BytesIO(b'mock image content'), 'test_image.jpg')

    @patch('app.collection')  # Mock MongoDB collection
    @patch('app.rf_client')   # Mock Roboflow client
    def test_successful_prediction(self, mock_rf_client, mock_collection):
        """Test successful prediction path"""
        # Mock Roboflow response
        mock_prediction = {
            "predictions": [{
                "class": "rock",
                "confidence": 0.95
            }]
        }
        mock_rf_client.infer.return_value = mock_prediction
        
        # Mock MongoDB insert
        mock_collection.insert_one.return_value = MagicMock()
        
        # Create test data
        data = {'image': self.mock_image}
        
        # Test the endpoint
        with patch('os.makedirs') as mock_makedirs:
            with patch('builtins.open', mock_open()):
                response = self.client.post('/predict', 
                                         data=data,
                                         content_type='multipart/form-data')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['gesture'], 'rock')
        self.assertEqual(response_data['confidence'], 0.95)
        
        # Verify mocks were called
        mock_rf_client.infer.assert_called_once()
        mock_collection.insert_one.assert_called_once()
        mock_makedirs.assert_called_once_with('./temp', exist_ok=True)

    def test_missing_image(self):
        """Test prediction without providing an image"""
        response = self.client.post('/predict')
        
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'No image file provided')

    @patch('app.collection')
    @patch('app.rf_client')
    def test_unknown_gesture_prediction(self, mock_rf_client, mock_collection):
        """Test handling of unknown gesture predictions"""
        # Mock Roboflow response with unknown class
        mock_prediction = {
            "predictions": [{
                "class": "Unknown",
                "confidence": 0.3
            }]
        }
        mock_rf_client.infer.return_value = mock_prediction
        
        # Mock MongoDB insert
        mock_collection.insert_one.return_value = MagicMock()
        
        # Create test data
        data = {'image': self.mock_image}
        
        # Test the endpoint
        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()):
                response = self.client.post('/predict', 
                                         data=data,
                                         content_type='multipart/form-data')
        
        # Assert response
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertEqual(response_data['gesture'], 'Unknown')
        self.assertEqual(response_data['confidence'], 0)

    @patch('app.collection')
    @patch('app.rf_client')
    def test_roboflow_api_error(self, mock_rf_client, mock_collection):
        """Test handling of Roboflow API errors"""
        # Mock Roboflow error
        mock_rf_client.infer.side_effect = RequestException("API Error")
        
        # Create test data
        data = {'image': self.mock_image}
        
        # Test the endpoint
        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()):
                response = self.client.post('/predict', 
                                         data=data,
                                         content_type='multipart/form-data')
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('API Error', response_data['error'])

    @patch('app.collection')
    @patch('app.rf_client')
    def test_mongodb_error(self, mock_rf_client, mock_collection):
        """Test handling of MongoDB errors"""
        # Mock successful Roboflow prediction
        mock_prediction = {
            "predictions": [{
                "class": "rock",
                "confidence": 0.95
            }]
        }
        mock_rf_client.infer.return_value = mock_prediction
        
        # Mock MongoDB error
        mock_collection.insert_one.side_effect = PyMongoError("Database Error")
        
        # Create test data
        data = {'image': self.mock_image}
        
        # Test the endpoint
        with patch('os.makedirs'):
            with patch('builtins.open', mock_open()):
                response = self.client.post('/predict', 
                                         data=data,
                                         content_type='multipart/form-data')
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('Database Error', response_data['error'])

    @patch('app.collection')
    @patch('app.rf_client')
    def test_file_system_error(self, mock_rf_client, mock_collection):
        """Test handling of file system errors"""
        # Mock file system error
        mock_open_impl = mock_open()
        mock_open_impl.side_effect = FileNotFoundError("File system error")
        
        # Create test data
        data = {'image': self.mock_image}
        
        # Test the endpoint
        with patch('os.makedirs'):
            with patch('builtins.open', mock_open_impl):
                response = self.client.post('/predict', 
                                         data=data,
                                         content_type='multipart/form-data')
        
        # Assert response
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.data)
        self.assertIn('error', response_data)
        self.assertIn('File system error', response_data['error'])

if __name__ == '__main__':
    unittest.main()


