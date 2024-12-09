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
from io import BytesIO
from bson.objectid import ObjectId
import mongomock
from app import app, socketio, determine_winners, determine_ai_winner
from flask_socketio import SocketIOTestClient

# Configure Flask app for testing
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# Mock MongoDB using mongomock
@pytest.fixture(autouse=True)
def mock_mongo(monkeypatch):
    mock_client = mongomock.MongoClient()
    monkeypatch.setattr("app.MongoClient", lambda uri: mock_client)
    return mock_client

# Mock the ML client (client.py's /predict endpoint)
@pytest.fixture
def mock_ml_predict():
    with patch("app.retry_request") as mock:
        yield mock

# Configure SocketIO for testing
@pytest.fixture
def socketio_client():
    client = socketio.test_client(app, flask_test_client=client)
    yield client
    client.disconnect()

# Helper fixture to initialize a stats document and set cookie
@pytest.fixture
def initialize_stats(client):
    # Insert a stats document
    mock_db = mongomock.MongoClient().rps_database.stats
    stats_doc = {
        "_id": ObjectId(),
        "Rock": {"wins": 0, "losses": 0, "ties": 0, "total": 0},
        "Paper": {"wins": 0, "losses": 0, "ties": 0, "total": 0},
        "Scissors": {"wins": 0, "losses": 0, "ties": 0, "total": 0},
        "Totals": {"wins": 0, "losses": 0, "ties": 0},
    }
    mock_db.insert_one(stats_doc)
    # Set the cookie
    client.set_cookie("localhost", "db_object_id", str(stats_doc["_id"]))
    return stats_doc["_id"]

# Test the home route
def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"title.html" not in response.data  # Assuming template rendering

# Test the ai route
def test_ai_route(client):
    response = client.get("/ai")
    assert response.status_code == 200
    assert b"ai.html" not in response.data  # Assuming template rendering

# Test the ai_machine_learning route
def test_ai_ml_route(client):
    response = client.get("/ai_machine_learning")
    assert response.status_code == 200
    assert b"ai_machine_learning.html" not in response.data  # Assuming template rendering

# Test the real_person route
def test_real_person_route(client):
    response = client.get("/real_person")
    assert response.status_code == 200
    assert b"real_person.html" not in response.data  # Assuming template rendering

# Test the /result route successfully
def test_result_success(client, mock_ml_predict, initialize_stats):
    mock_ml_predict.return_value = MagicMock()
    mock_ml_predict.return_value.json.return_value = {"gesture": "rock"}

    data = {
        "image": (BytesIO(b"fake image data"), "test_image.jpg")
    }

    response = client.post("/result", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["user_gesture"] == "rock"
    assert json_data["ai_choice"] in ["rock", "paper", "scissors"]
    assert json_data["result"] in ["It's a tie!", "You win!", "AI wins!"]

# Test the /result route with no image
def test_result_no_image(client):
    response = client.post("/result", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "No image file provided"

# Test the /result route with ML client failure
def test_result_ml_failure(client, mock_ml_predict):
    mock_ml_predict.return_value = None  # Simulate ML client not responding

    data = {
        "image": (BytesIO(b"fake image data"), "test_image.jpg")
    }

    response = client.post("/result", data=data, content_type="multipart/form-data")
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data["error"] == "ML client did not respond"

# Test the /result route with invalid ML response
def test_result_invalid_ml_response(client, mock_ml_predict):
    mock_response = MagicMock()
    mock_response.json.return_value = {"invalid_key": "value"}
    mock_ml_predict.return_value = mock_response

    data = {
        "image": (BytesIO(b"fake image data"), "test_image.jpg")
    }

    response = client.post("/result", data=data, content_type="multipart/form-data")
    assert response.status_code == 500
    json_data = response.get_json()
    assert "Invalid response from ML client" in json_data["error"]

# Test the /play/ai route successfully
def test_play_against_ai_success(client):
    payload = {
        "player_name": "TestPlayer",
        "choice": "rock"
    }
    response = client.post("/play/ai", json=payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["player_name"] == "TestPlayer"
    assert json_data["player_choice"] == "rock"
    assert json_data["ai_choice"] in ["rock", "paper", "scissors"]
    assert json_data["result"] in ["win", "lose", "tie"]
    assert "stats" in json_data

# Test the /play/ai route with invalid choice
def test_play_against_ai_invalid_choice(client):
    payload = {
        "player_name": "TestPlayer",
        "choice": "invalid_choice"
    }
    response = client.post("/play/ai", json=payload)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Invalid choice"

# Test the determine_winners function
def test_determine_winners():
    result = determine_winners("rock", "scissors")
    assert result == "You win!"

    result = determine_winners("rock", "paper")
    assert result == "AI wins!"

    result = determine_winners("rock", "rock")
    assert result == "It's a tie!"

# Test the determine_ai_winner function
def test_determine_ai_winner():
    result = determine_ai_winner("rock", "scissors")
    assert result == "win"

    result = determine_ai_winner("rock", "paper")
    assert result == "lose"

    result = determine_ai_winner("rock", "rock")
    assert result == "tie"

# Socket.IO Event Tests

# Fixture for Socket.IO test client
@pytest.fixture
def sio_client():
    with socketio.test_client(app, flask_test_client=client) as sio:
        yield sio

# Test Socket.IO random_match event - Player waits when no opponents
def test_socketio_random_match_waiting(sio_client):
    with patch("app.waiting_players", []), \
         patch("app.active_games", {}), \
         patch("app.socketio.start_background_task") as mock_start_bg_task:
        
        sio_client.emit("random_match", {"player_name": "Player1", "player_id": "id1"})
        received = sio_client.get_received()
        
        # Expect a "waiting" event since no opponent is available
        assert len(received) == 1
        assert received[0]['name'] == 'waiting'
        assert received[0]['args'][0]['message'] == "Waiting for an opponent..."

# Test Socket.IO random_match event - Matchmaking when a player is waiting
def test_socketio_random_match_match_found(sio_client):
    with patch("app.waiting_players", [{"player_id": "id1", "player_name": "Player1", "sid": "sid1"}]), \
         patch("app.active_games", {}) as mock_active_games, \
         patch("app.socketio.start_background_task") as mock_start_bg_task:
        
        sio_client.emit("random_match", {"player_name": "Player2", "player_id": "id2"})
        received = sio_client.get_received()
        
        # Expect two "match_found" events: one for each player
        assert len(received) == 2
        assert received[0]['name'] == 'match_found'
        assert received[0]['args'][0]['opponent'] == "Player1"
        assert received[1]['name'] == 'match_found'
        assert received[1]['args'][0]['opponent'] == "Player2"
        
        # Ensure a game is added to active_games
        assert len(mock_active_games) == 1
        game_id = list(mock_active_games.keys())[0]
        game = mock_active_games[game_id]
        assert game['player1_id'] == "id1"
        assert game['player2_id'] == "id2"
        
        # Ensure countdown_timer is started
        mock_start_bg_task.assert_called_once()

# Test Socket.IO cancel_waiting event
def test_socketio_cancel_waiting(sio_client):
    with patch("app.waiting_players", [{"player_id": "id1", "player_name": "Player1", "sid": "sid1"}]):
        sio_client.emit("cancel_waiting", {"player_id": "id1"})
        received = sio_client.get_received()
        
        # Expect a "waiting_cancelled" event
        assert len(received) == 1
        assert received[0]['name'] == 'waiting_cancelled'
        assert received[0]['args'][0]['message'] == "You canceled waiting for an opponent."

# Test Socket.IO cancel_match event
def test_socketio_cancel_match(sio_client):
    with patch("app.active_games", {"game123": {
        "player1_id": "id1",
        "player2_id": "id2",
        "player1_sid": "sid1",
        "player2_sid": "sid2",
        "player1_name": "Player1",
        "player2_name": "Player2",
        "ready": {"player1": False, "player2": False},
    }}), \
    patch("app.reset_game_state") as mock_reset_game_state:
        
        sio_client.emit("cancel_match", {"game_id": "game123", "player_id": "id1"})
        received = sio_client.get_received()
        
        # Expect a "match_cancelled" event
        assert len(received) == 1
        assert received[0]['name'] == 'match_cancelled'
        assert received[0]['args'][0]['message'] == "Match canceled by Player1."
        
        # Ensure the game is removed
        assert "game123" not in app.active_games
        
        # Ensure reset_game_state is called
        mock_reset_game_state.assert_called_once_with("game123")

# Test Socket.IO start_game event
def test_socketio_start_game(sio_client):
    with patch("app.active_games", {"game123": {
        "player1_id": "id1",
        "player2_id": "id2",
        "player1_sid": "sid1",
        "player2_sid": "sid2",
        "player1_name": "Player1",
        "player2_name": "Player2",
        "ready": {"player1": False, "player2": False},
    }}), \
    patch("app.join_room") as mock_join_room:
        
        # Player1 signals readiness
        sio_client.emit("start_game", {"game_id": "game123", "player_id": "id1"})
        received = sio_client.get_received()
        assert len(received) == 0  # No immediate response
        
        # Check if player1 is marked as ready
        game = app.active_games["game123"]
        assert game["ready"]["player1"] == True
        
        # Player2 signals readiness
        sio_client.emit("start_game", {"game_id": "game123", "player_id": "id2"})
        received = sio_client.get_received()
        
        # Expect a "proceed_to_game" event
        assert len(received) == 1
        assert received[0]['name'] == 'proceed_to_game'
        assert received[0]['args'][0]['message'] == "Both players are ready! Starting the game..."
        
        # Ensure both players have joined the room
        mock_join_room.assert_called()

# Test Socket.IO join_game event
def test_socketio_join_game(sio_client):
    with patch("app.active_games", {"game123": {
        "player1_id": "id1",
        "player2_id": "id2",
        "player1_sid": "sid1",
        "player2_sid": "sid2",
        "player1_name": "Player1",
        "player2_name": "Player2",
    }}), \
    patch("app.join_room") as mock_join_room, \
    patch("app.socketio.emit") as mock_emit:
        
        sio_client.emit("join_game", {"game_id": "game123", "player_id": "id1"})
        received = sio_client.get_received()
        
        # Expect a "start_game" event
        assert len(received) == 1
        assert received[0]['name'] == 'start_game'
        assert received[0]['args'][0]['message'] == "Game starting soon!"
        
        # Ensure player1 has joined the room
        mock_join_room.assert_called_with("game123")
        mock_emit.assert_called_with("start_game", {"message": "Game starting soon!"}, room="game123")

# Test Socket.IO submit_choice event
def test_socketio_submit_choice(sio_client):
    with patch("app.active_games", {"game123": {
        "player1_id": "id1",
        "player2_id": "id2",
        "player1_sid": "sid1",
        "player2_sid": "sid2",
        "player1_name": "Player1",
        "player2_name": "Player2",
        "player1_choice": None,
        "player2_choice": None,
    }}), \
    patch("app.socketio.emit") as mock_emit:
        
        # Player1 submits choice
        sio_client.emit("submit_choice", {"game_id": "game123", "player_id": "id1", "choice": "rock"})
        received = sio_client.get_received()
        assert len(received) == 0  # No immediate response
        
        # Player2 submits choice
        sio_client.emit("submit_choice", {"game_id": "game123", "player_id": "id2", "choice": "scissors"})
        received = sio_client.get_received()
        
        # Expect a "game_result" event
        assert len(received) == 1
        assert received[0]['name'] == 'game_result'
        game_result = received[0]['args'][0]
        assert game_result["player1_name"] == "Player1"
        assert game_result["player2_name"] == "Player2"
        assert game_result["player1_choice"] == "rock"
        assert game_result["player2_choice"] == "scissors"
        assert game_result["result"] == "Player1 wins!"

# Test Socket.IO disconnect event
def test_socketio_disconnect(sio_client):
    with patch("app.active_games", {"game123": {
        "player1_id": "id1",
        "player2_id": "id2",
        "player1_sid": "sid1",
        "player2_sid": "sid2",
        "player1_name": "Player1",
        "player2_name": "Player2",
    }}):
        
        # Simulate disconnect
        sio_client.disconnect()
        
        # The disconnect handler should remove the player from active_games
        # Depending on implementation, you might need to check the state
        # Here we assume that if a player disconnects, their sid is set to None
        game = app.active_games["game123"]
        assert game["player1_sid"] is None or game["player2_sid"] is None

# Additional Tests

# Test the countdown_timer function
def test_countdown_timer():
    # Since countdown_timer runs in a background task, it might be complex to test directly
    # Instead, you can ensure that the countdown emits events correctly
    pass  # Implementation depends on the testing framework's support for async tasks

# Test the handle_start_game event with invalid game ID
def test_socketio_start_game_invalid_game(sio_client):
    sio_client.emit("start_game", {"game_id": "invalid_game", "player_id": "id1"})
    received = sio_client.get_received()
    
    # Expect an "error" event
    assert len(received) == 1
    assert received[0]['name'] == 'error'
    assert received[0]['args'][0]['message'] == "Invalid game ID."

# Test the handle_submit_choice event with invalid player ID
def test_socketio_submit_choice_invalid_player(sio_client):
    with patch("app.active_games", {"game123": {
        "player1_id": "id1",
        "player2_id": "id2",
        "player1_sid": "sid1",
        "player2_sid": "sid2",
        "player1_name": "Player1",
        "player2_name": "Player2",
        "player1_choice": None,
        "player2_choice": None,
    }}):
        sio_client.emit("submit_choice", {"game_id": "game123", "player_id": "invalid_id", "choice": "rock"})
        received = sio_client.get_received()
        
        # Expect an "error" event
        assert len(received) == 1
        assert received[0]['name'] == 'error'
        assert received[0]['args'][0]['message'] == "Invalid player ID."

# Test the /statistics route
def test_statistics_route(client, initialize_stats):
    response = client.get("/statistics")
    assert response.status_code == 200
    assert b"Statistics" in response.data
    # Additional checks can be performed based on the rendered template

# Test generate_stats_doc function
def test_generate_stats_doc(client):
    with patch("app.collection.insert_one") as mock_insert:
        mock_insert.return_value.inserted_id = ObjectId()
        response = client.get("/")
        mock_insert.assert_called_once()
        # Check if cookie is set
        assert "db_object_id" in response.headers["Set-Cookie"]

# Test the retry_request function
def test_retry_request_success_on_first_try(client, mock_ml_predict):
    mock_ml_predict.return_value = MagicMock()
    mock_ml_predict.return_value.json.return_value = {"gesture": "rock"}

    data = {
        "image": (BytesIO(b"fake image data"), "test_image.jpg")
    }

    response = client.post("/result", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
