"""
Unit tests for the Flask application defined in `app.py`.
"""

# test_app.py
# cd web-app
# pytest test_app.py -v
# pytest -v

# pylint web-app/
# black .

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO

# Mock the eventlet import in app.py
import sys
import mock
sys.modules['eventlet'] = MagicMock()
sys.modules['eventlet.monkey_patch'] = MagicMock()

# Now import the app
from app import app

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_mongodb():
    """Mock MongoDB client"""
    with patch('app.client') as mock_client:
        yield mock_client

# Test HTTP Routes
def test_home_page(client):
    """Test the home page route"""
    response = client.get('/')
    assert response.status_code == 200

def test_ai_page(client):
    """Test the AI game page route"""
    response = client.get('/ai')
    assert response.status_code == 200

def test_ai_ml_page(client):
    """Test the AI ML game page route"""
    response = client.get('/ai_machine_learning')
    assert response.status_code == 200

def test_real_person_page(client):
    """Test the real person game page route"""
    response = client.get('/real_person')
    assert response.status_code == 200

# Test Game Logic
def test_determine_winners():
    """Test the determine_winners function"""
    from app import determine_winners
    assert determine_winners('rock', 'scissors') == 'You win!'
    assert determine_winners('rock', 'paper') == 'AI wins!'
    assert determine_winners('rock', 'rock') == "It's a tie!"

def test_determine_ai_winner():
    """Test the determine_ai_winner function"""
    from app import determine_ai_winner
    assert determine_ai_winner('rock', 'scissors') == 'win'
    assert determine_ai_winner('rock', 'paper') == 'lose'
    assert determine_ai_winner('rock', 'rock') == 'tie'

# Test AI Play Route
def test_play_against_ai_valid(client):
    """Test playing against AI with valid input"""
    response = client.post('/play/ai', 
                         json={'player_name': 'Test', 'choice': 'rock'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert all(key in data for key in ['player_name', 'player_choice', 'ai_choice', 'result', 'stats'])

def test_play_against_ai_invalid(client):
    """Test playing against AI with invalid input"""
    response = client.post('/play/ai', 
                         json={'player_name': 'Test', 'choice': 'invalid'})
    assert response.status_code == 400

# Test Result Route
@patch('app.retry_request')
def test_result_endpoint_success(mock_retry, client):
    """Test the result endpoint with successful ML client response"""
    mock_response = MagicMock()
    mock_response.json.return_value = {'gesture': 'rock'}
    mock_response.status_code = 200
    mock_retry.return_value = mock_response

    data = {'image': (BytesIO(b'test image data'), 'test.jpg')}
    response = client.post('/result', data=data)
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert all(key in result for key in ['user_gesture', 'ai_choice', 'result'])

def test_result_endpoint_no_image(client):
    """Test the result endpoint with no image"""
    response = client.post('/result')
    assert response.status_code == 400
    assert b'No image file provided' in response.data

def test_result_endpoint_empty_file(client):
    """Test the result endpoint with empty file"""
    data = {'image': (BytesIO(b''), '')}
    response = client.post('/result', data=data)
    assert response.status_code == 400

@patch('app.retry_request')
def test_result_endpoint_ml_failure(mock_retry, client):
    """Test the result endpoint when ML client fails"""
    mock_retry.return_value = None
    
    data = {'image': (BytesIO(b'test image data'), 'test.jpg')}
    response = client.post('/result', data=data)
    
    assert response.status_code == 500
    result = json.loads(response.data)
    assert 'error' in result

def test_retry_request():
    """Test retry request function"""
    from app import retry_request
    mock_files = {'image': MagicMock()}
    mock_files['image'].stream = BytesIO(b'test')
    
    with patch('requests.post') as mock_post:
        # Test successful request
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        result = retry_request('http://test.com', mock_files)
        assert result == mock_response

        # Test failed request with retries
        mock_post.side_effect = Exception('Test error')
        result = retry_request('http://test.com', mock_files, retries=2, delay=0)
        assert result is None
