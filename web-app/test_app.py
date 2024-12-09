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
from flask_socketio import SocketIOTestClient
from app import app, socketio, active_games, waiting_players, player_stats
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
def socket_client():
    """SocketIO test client"""
    app.config['TESTING'] = True
    return SocketIOTestClient(app, socketio)

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

# Test Result Route
@patch('app.requests.post')
def test_result_endpoint_success(mock_post, client):
    """Test the result endpoint with successful ML client response"""
    mock_response = MagicMock()
    mock_response.json.return_value = {'gesture': 'rock'}
    mock_response.status_code = 200
    mock_post.return_value = mock_response

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

# Test Socket.IO Events
def test_random_match(socket_client):
    """Test random match functionality"""
    socket_client.emit('random_match', {
        'player_name': 'Player1',
        'player_id': '123'
    })
    received = socket_client.get_received()
    assert len(received) > 0
    assert received[0]['name'] == 'waiting'

def test_cancel_waiting(socket_client):
    """Test canceling waiting for match"""
    socket_client.emit('cancel_waiting', {'player_id': '123'})
    received = socket_client.get_received()
    assert len(received) > 0
    assert received[0]['name'] == 'waiting_cancelled'

def test_start_game(socket_client):
    """Test starting a game"""
    # Setup a mock game
    game_id = '123'
    active_games[game_id] = {
        'player1_id': '1',
        'player2_id': '2',
        'ready': {'player1': False, 'player2': False}
    }
    
    socket_client.emit('start_game', {
        'game_id': game_id,
        'player_id': '1'
    })
    received = socket_client.get_received()
    assert len(received) > 0

def test_submit_choice(socket_client):
    """Test submitting a choice in game"""
    game_id = '123'
    active_games[game_id] = {
        'player1_id': '1',
        'player2_id': '2',
        'player1_name': 'Player1',
        'player2_name': 'Player2',
        'player1_choice': None,
        'player2_choice': None
    }
    
    socket_client.emit('submit_choice', {
        'game_id': game_id,
        'player_id': '1',
        'choice': 'rock'
    })
    
    assert active_games[game_id]['player1_choice'] == 'rock'

# Test Error Handling
def test_handle_disconnect(socket_client):
    """Test disconnect handling"""
    game_id = '123'
    active_games[game_id] = {
        'player1_sid': socket_client.sid,
        'player2_sid': 'other_sid'
    }
    
    socket_client.disconnect()
    
    assert active_games[game_id]['player1_sid'] is None

def test_retry_request():
    """Test retry request function"""
    from app import retry_request
    mock_files = {'image': MagicMock()}
    mock_files['image'].stream = BytesIO(b'test')
    
    with patch('app.requests.post') as mock_post:
        mock_post.side_effect = Exception('Test error')
        result = retry_request('http://test.com', mock_files, retries=2, delay=0)
        assert result is None
        assert mock_post.call_count == 2


