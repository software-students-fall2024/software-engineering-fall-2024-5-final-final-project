"""
Unit tests for the Flask application defined in `app.py`.
"""

# test_app.py
# cd web-app
# pytest test_app.py -v
# pytest -v

# pylint web-app/
# black .

import pytest
from unittest.mock import patch, MagicMock

# Mock eventlet before importing app
with patch('eventlet.monkey_patch'):
    from app import app, active_games, waiting_players, player_stats

from io import BytesIO
import json
import os

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

# Test Game Logic Functions
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

def test_update_player_stats():
    """Test the update_player_stats function"""
    from app import update_player_stats
    initial_stats = player_stats.copy()
    
    update_player_stats('win')
    assert player_stats['wins'] == initial_stats['wins'] + 1
    
    update_player_stats('lose')
    assert player_stats['losses'] == initial_stats['losses'] + 1
    
    update_player_stats('tie')
    assert player_stats['ties'] == initial_stats['ties'] + 1

# Test AI Play Route
def test_play_against_ai_valid(client):
    """Test playing against AI with valid input"""
    response = client.post('/play/ai', 
                         json={'player_name': 'Test', 'choice': 'rock'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'player_name' in data
    assert 'player_choice' in data
    assert 'ai_choice' in data
    assert 'result' in data
    assert 'stats' in data

def test_play_against_ai_invalid(client):
    """Test playing against AI with invalid input"""
    response = client.post('/play/ai', 
                         json={'player_name': 'Test', 'choice': 'invalid'})
    assert response.status_code == 400

# Test Result Route with mocked retry_request
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
    assert 'user_gesture' in result
    assert 'ai_choice' in result
    assert 'result' in result

def test_result_endpoint_no_image(client):
    """Test the result endpoint with no image"""
    response = client.post('/result')
    assert response.status_code == 400

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
        assert mock_post.call_count == 3  # Initial try + 2 retries

def test_determine_winner():
    """Test the multiplayer winner determination"""
    from app import determine_winner
    assert determine_winner('rock', 'scissors', 'Player1', 'Player2') == 'Player1 wins!'
    assert determine_winner('rock', 'paper', 'Player1', 'Player2') == 'Player2 wins!'
    assert determine_winner('rock', 'rock', 'Player1', 'Player2') == 'tie'

def test_reset_game():
    """Test game reset functionality"""
    from app import reset_game
    game_id = 'test_game'
    active_games[game_id] = {
        'player1_choice': 'rock',
        'player2_choice': 'paper'
    }
    reset_game(game_id)
    assert active_games[game_id]['player1_choice'] is None
    assert active_games[game_id]['player2_choice'] is None
