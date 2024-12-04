import eventlet
eventlet.monkey_patch()
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect, join_room
from uuid import uuid4
import random
from threading import Lock

# Initialize Flask and Socket.IO
app = Flask(__name__, template_folder="../templates", static_folder="../static")
socketio = SocketIO(app)

# In-memory data
waiting_players = []
active_games = {}
matchmaking_lock = Lock()
player_stats = {"wins": 0, "losses": 0, "ties": 0} 
# ----------- ROUTES -----------

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')


@app.route('/ai')
def ai_page():
    """Render the AI game page."""
    return render_template('ai.html')


@app.route('/real_person')
def real_person_page():
    """Render the real person game page."""
    return render_template('real_person.html')


@app.route('/play/ai', methods=['POST'])
def play_against_ai():
    """
    Handle the game logic for playing against AI.
    """
    data = request.json
    player_name = data.get('player_name', 'Player') 
    player_choice = data.get('choice')

    if player_choice not in ['rock', 'paper', 'scissor']:
        return jsonify({"error": "Invalid choice"}), 400
    ai_choice = random.choice(['rock', 'paper', 'scissor'])
    result = determine_ai_winner(player_choice, ai_choice)
    update_player_stats(result)

    return jsonify({
        "player_name": player_name,
        "player_choice": player_choice,
        "ai_choice": ai_choice,
        "result": result,
        "stats": player_stats
    })

def determine_ai_winner(player_choice, ai_choice):
    """
    Determine the winner for AI games.
    """
    outcomes = {
        "rock": {"rock": "tie", "paper": "lose", "scissor": "win"},
        "paper": {"rock": "win", "paper": "tie", "scissor": "lose"},
        "scissor": {"rock": "lose", "paper": "win", "scissor": "tie"}
    }
    return outcomes[player_choice][ai_choice]

def update_player_stats(result):
    """
    Update the player's stats based on the result of the game.
    """
    if result == 'win':
        player_stats['wins'] += 1
    elif result == 'lose':
        player_stats['losses'] += 1
    elif result == 'tie':
        player_stats['ties'] += 1

# ----------- MATCHMAKING -----------

@socketio.on("random_match")
def handle_random_match(data):
    """Handle random matchmaking."""
    player_name = data.get("player_name")
    player_id = data.get("player_id")
    sid = request.sid

    if not player_name or not player_id:
        emit("error", {"message": "Player name and ID are required."})
        return

    with matchmaking_lock:
        if waiting_players:
            # Match with an opponent
            opponent = waiting_players.pop(0)
            game_id = str(uuid4())
            active_games[game_id] = {
                "player1_id": opponent["player_id"],
                "player2_id": player_id,
                "player1_sid": opponent["sid"],
                "player2_sid": sid,
                "player1_choice": None,
                "player2_choice": None,
                "player1_name": opponent["player_name"],
                "player2_name": player_name,
            }
            emit("match_found", {"game_id": game_id, "opponent": opponent["player_name"]}, to=sid)
            emit("match_found", {"game_id": game_id, "opponent": player_name}, to=opponent["sid"])
        else:
            # Add to waiting queue
            waiting_players.append({"player_id": player_id, "player_name": player_name, "sid": sid})
            emit("waiting", {"message": "Waiting for an opponent..."}, to=sid)


@socketio.on("join_game")
def handle_join_game(data):
    """Handle a player joining a specific game."""
    game_id = data.get("game_id")
    player_id = data.get("player_id")
    sid = request.sid

    if not game_id or not player_id:
        emit("error", {"message": "Game ID and Player ID are required."})
        return

    if game_id not in active_games:
        emit("error", {"message": "Invalid game ID."})
        return

    game = active_games[game_id]
    
    if game["player1_id"] == player_id:
        game["player1_sid"] = sid  # Update session ID
        join_room(game_id)
        emit("start_game", {"player_role": "player1"}, to=sid)
    elif game["player2_id"] == player_id:
        game["player2_sid"] = sid  # Update session ID
        join_room(game_id)
        emit("start_game", {"player_role": "player2"}, to=sid)
    else:
        emit("error", {"message": "You are not part of this game."})

# ----------- GAMEPLAY -----------
@socketio.on("submit_choice")
def handle_submit_choice(data):
    """Handle a player's choice submission."""
    game_id = data.get("game_id")
    player_id = data.get("player_id")
    choice = data.get("choice")
    
    if game_id not in active_games:
        emit("error", {"message": "Invalid game ID."})
        return

    game = active_games[game_id]

    if player_id == game["player1_id"]:
        game["player1_choice"] = choice
    elif player_id == game["player2_id"]:
        game["player2_choice"] = choice
    else:
        emit("error", {"message": "Invalid player ID."})
        return

    # Check if both players have made their choices
    if game["player1_choice"] and game["player2_choice"]:
        print(f"Choices: {game['player1_choice']}, {game['player2_choice']}")  # Debugging
        result = determine_winner(
            game["player1_choice"],
            game["player2_choice"],
            game["player1_name"],
            game["player2_name"]
        )

        # Send the result to both players in the game room
        socketio.emit("game_result", {
            "player1_name": game["player1_name"],
            "player2_name": game["player2_name"],
            "player1_choice": game["player1_choice"],
            "player2_choice": game["player2_choice"],
            "result": result,
        }, room=game_id)

        # Reset the game
        reset_game(game_id)


def reset_game(game_id):
    """Reset the game state."""
    if game_id in active_games:
        active_games[game_id]["player1_choice"] = None
        active_games[game_id]["player2_choice"] = None


def determine_winner(player1_choice, player2_choice, player1_name, player2_name):
    """Determine the winner for a multiplayer game."""
    outcomes = {
        "rock": {"rock": "tie", "paper": f"{player2_name} wins!", "scissor": f"{player1_name} wins!"},
        "paper": {"rock": f"{player1_name} wins!", "paper": "tie", "scissor": f"{player2_name} wins!"},
        "scissor": {"rock": f"{player2_name} wins!", "paper": f"{player1_name} wins!", "scissor": "tie"},
    }
    return outcomes[player1_choice][player2_choice]


@socketio.on("disconnect")
def handle_disconnect():
    """Handle player disconnection."""
    sid = request.sid
    for game_id, game in list(active_games.items()):
        if game["player1_sid"] == sid:
            game["player1_sid"] = None
        elif game["player2_sid"] == sid:
            game["player2_sid"] = None

        # Clean up the game if both players are disconnected
        if not game["player1_sid"] and not game["player2_sid"]:
            del active_games[game_id]

# ----------- START THE SERVER -----------
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=True)