"""
Unit tests for the Flask application defined in `app.py`.
"""

# test_app.py
# cd web-app
# pytest test_app.py -v
# pytest -v

# python -m pytest test_app.py -v

# pylint web-app/
# black .

"""
Unit tests for the Flask application defined in `app.py`.
"""

import os
import json
import pytest
from unittest.mock import patch, MagicMock
from io import BytesIO
from requests.exceptions import RequestException

# Mock the eventlet module
import sys
eventlet_mock = MagicMock()
eventlet_mock.monkey_patch = MagicMock()
sys.modules['eventlet'] = eventlet_mock

# Now import the app after mocking eventlet
from app import (
    app, determine_winners, determine_ai_winner, retry_request,
    active_games, waiting_players, player_stats
)

@pytest.fixture
def client():
    """Flask test client"""
    app.config['TESTING'] = True
    with app.test_client() as test_client:
        yield test_client

@pytest.fixture
def mock_mongodb(monkeypatch):
    """Mock MongoDB client using mongomock"""
    import mongomock
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr("app.MongoClient", lambda uri: mock_client)
    return mock_client

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Reset game state before each test"""
    active_games.clear()
    waiting_players.clear()
    player_stats.update({"wins": 0, "losses": 0, "ties": 0})
    yield

# Test HTTP Routes
def test_home_page(client):
    """Test the home page route"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Home" in response.data  # Updated based on your template

def test_ai_page(client):
    """Test the AI game page route"""
    response = client.get('/ai')
    assert response.status_code == 200
    assert b"AI Game" in response.data

def test_ai_ml_page(client):
    """Test the AI ML game page route"""
    response = client.get('/ai_machine_learning')
    assert response.status_code == 200
    assert b"Machine Learning" in response.data

def test_real_person_page(client):
    """Test the real person game page route"""
    response = client.get('/real_person')
    assert response.status_code == 200
    assert b"Multiplayer" in response.data

# Test Game Logic
def test_determine_winners_comprehensive():
    """Test all combinations for determine_winners function"""
    test_cases = [
        ('rock', 'scissors', 'You win!'),
        ('rock', 'paper', 'AI wins!'),
        ('rock', 'rock', "It's a tie!"),
        ('paper', 'rock', 'You win!'),
        ('paper', 'scissors', 'AI wins!'),
        ('paper', 'paper', "It's a tie!"),
        ('scissors', 'paper', 'You win!'),
        ('scissors', 'rock', 'AI wins!'),
        ('scissors', 'scissors', "It's a tie!")
    ]
    for player, ai, expected in test_cases:
        assert determine_winners(player, ai) == expected

def test_determine_ai_winner_comprehensive():
    """Test all combinations for determine_ai_winner function"""
    test_cases = [
        ('rock', 'scissors', 'win'),
        ('rock', 'paper', 'lose'),
        ('rock', 'rock', 'tie'),
        ('paper', 'rock', 'win'),
        ('paper', 'scissors', 'lose'),
        ('paper', 'paper', 'tie'),
        ('scissors', 'paper', 'win'),
        ('scissors', 'rock', 'lose'),
        ('scissors', 'scissors', 'tie')
    ]
    for player, ai, expected in test_cases:
        assert determine_ai_winner(player, ai) == expected

def test_update_player_stats_comprehensive():
    """Test player stats updates"""
    from app import update_player_stats
    
    test_cases = [('win', 'wins'), ('lose', 'losses'), ('tie', 'ties')]
    for result, stat_key in test_cases:
        initial_value = player_stats[stat_key]
        update_player_stats(result)
        assert player_stats[stat_key] == initial_value + 1
        
        # Check other stats didn't change
        other_keys = set(['wins', 'losses', 'ties']) - {stat_key}
        for other_key in other_keys:
            assert player_stats[other_key] == 0

# Test AI Play Route
def test_play_against_ai_missing_data(client):
    """Test playing against AI with missing data"""
    test_cases = [
        ({}, 400),
        ({'player_name': 'Test'}, 400),
        ({'choice': 'rock'}, 400),
        ({'player_name': '', 'choice': 'rock'}, 400)
    ]
    for data, expected_status in test_cases:
        response = client.post('/play/ai', json=data)
        assert response.status_code == expected_status

def test_play_against_ai_valid_comprehensive(client, mock_mongodb):
    """Test all valid combinations for AI play"""
    choices = ['rock', 'paper', 'scissors']
    for choice in choices:
        response = client.post('/play/ai', 
                             json={'player_name': 'Test', 'choice': choice})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['player_choice'] == choice
        assert data['ai_choice'] in choices
        assert data['result'] in ['win', 'lose', 'tie']

# Test Result Route - Additional Cases
@patch('app.retry_request')
def test_result_endpoint_invalid_response(mock_retry, client):
    """Test handling of invalid response from ML client"""
    mock_response = MagicMock()
    mock_response.json.return_value = {'invalid': 'response'}
    mock_response.status_code = 200
    mock_retry.return_value = mock_response

    data = {'image': (BytesIO(b'test image data'), 'test.jpg')}
    response = client.post('/result', data=data)
    
    assert response.status_code == 500

@patch('app.retry_request')
def test_result_endpoint_unknown_gesture(mock_retry, client):
    """Test handling of unknown gesture from ML client"""
    mock_response = MagicMock()
    mock_response.json.return_value = {'gesture': 'unknown'}
    mock_response.status_code = 200
    mock_retry.return_value = mock_response

    data = {'image': (BytesIO(b'test image data'), 'test.jpg')}
    response = client.post('/result', data=data)
    
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['user_gesture'] == 'unknown'

def test_retry_request_comprehensive():
    """Test retry_request function comprehensively"""
    mock_files = {'image': MagicMock()}
    mock_files['image'].stream = BytesIO(b'test')
    
    with patch('requests.post') as mock_post:
        # Test with different numbers of retries
        for retries in [1, 3, 5]:
            mock_post.side_effect = [RequestException("Error")] * retries
            result = retry_request('http://test.com', mock_files, 
                                 retries=retries, delay=0)
            assert result is None
            assert mock_post.call_count == retries
            mock_post.reset_mock()

        # Test with successful retry after failures
        mock_post.side_effect = [
            RequestException("Error"),
            RequestException("Error"),
            MagicMock(status_code=200)
        ]
        result = retry_request('http://test.com', mock_files, retries=3, delay=0)
        assert result is not None
        assert mock_post.call_count == 3

def test_file_cleanup_after_prediction():
    """Test that temporary files are cleaned up after prediction"""
    with app.test_client() as client:
        data = {'image': (BytesIO(b'test image data'), 'test.jpg')}
        with patch('app.retry_request') as mock_retry:
            mock_retry.return_value = MagicMock(
                json=lambda: {'gesture': 'rock'}
            )
            client.post('/result', data=data)
            # Verify temp directory is empty or file is removed
            assert not os.path.exists('./temp/test.jpg')
