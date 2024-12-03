import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, disconnect
from uuid import uuid4
import random
import time
from threading import Timer

# Initialize Flask and Socket.IO
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "your_secret_key"  # Replace with a secure key in production
socketio = SocketIO(app)

# In-memory data
waiting_players = []
active_games = {}
disconnect_grace_period = {}  # Store timers for players' grace periods

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


# ----------- MATCHMAKING -----------

@socketio.on("random_match")
def handle_random_match(data):
    """Handle random matchmaking."""
    player_name = data.get("player_name")
    sid = request.sid

    if not player_name:
        emit("match_error", {"error": "Player name is required."})
        return

    if waiting_players:
        # Match the current player with a waiting player
        opponent = waiting_players.pop(0)
        game_id = str(uuid4())

        # Store game details
        active_games[game_id] = {
            "player1_sid": opponent["sid"],
            "player2_sid": sid,
            "player1_choice": None,
            "player2_choice": None,
        }

        # Notify both players
        emit("match_found", {"game_id": game_id, "opponent": player_name}, to=opponent["sid"])
        emit("match_found", {"game_id": game_id, "opponent": opponent["player_name"]}, to=sid)
    else:
        # Add player to the waiting list
        waiting_players.append({"sid": sid, "player_name": player_name})
        emit("waiting", {"message": "Waiting for an opponent..."}, to=sid)


@socketio.on("join_game")
def handle_join_game(data):
    """Handle joining a specific game."""
    game_id = data.get("game_id")
    sid = request.sid

    if game_id not in active_games:
        emit("error", {"message": "Invalid game ID."})
        return

    game = active_games[game_id]

    # Check if the game is already full
    if sid in [game.get("player1_sid"), game.get("player2_sid")]:
        # If the same player reconnects, reassign their role
        if game.get("player1_sid") == sid:
            emit("start_game", {"player_role": "player1"}, to=sid)
        elif game.get("player2_sid") == sid:
            emit("start_game", {"player_role": "player2"}, to=sid)
        return

    if not game["player2_sid"]:
        # Assign the second player to the game
        game["player2_sid"] = sid
        emit("start_game", {"player_role": "player1"}, to=game["player1_sid"])
        emit("start_game", {"player_role": "player2"}, to=sid)
    else:
        emit("error", {"message": "Game is already full."})


@socketio.on("submit_choice")
def handle_submit_choice(data):
    """Handle submitting a choice during gameplay."""
    game_id = data.get("game_id")
    player = data.get("player")
    choice = data.get("choice")

    if game_id not in active_games:
        emit("error", {"message": "Invalid game ID."})
        return

    game = active_games[game_id]

    if player == "player1":
        game["player1_choice"] = choice
    elif player == "player2":
        game["player2_choice"] = choice

    if game["player1_choice"] and game["player2_choice"]:
        result = determine_winner(game["player1_choice"], game["player2_choice"])
        game["result"] = result

        emit("game_result", {
            "player1_choice": game["player1_choice"],
            "player2_choice": game["player2_choice"],
            "result": result,
        }, to=game["player1_sid"])

        emit("game_result", {
            "player1_choice": game["player1_choice"],
            "player2_choice": game["player2_choice"],
            "result": result,
        }, to=game["player2_sid"])

        # Clean up game after completion
        del active_games[game_id]


@socketio.on("disconnect")
def handle_disconnect():
    """Handle player disconnection with grace period."""
    sid = request.sid

    # Check if the player is in an active game
    for game_id, game in list(active_games.items()):
        if sid in [game["player1_sid"], game["player2_sid"]]:
            # Start a grace period
            def end_grace_period():
                """Finalize disconnection after the grace period."""
                if sid == game.get("player1_sid") or sid == game.get("player2_sid"):
                    opponent_sid = game["player2_sid"] if game["player1_sid"] == sid else game["player1_sid"]
                    emit("error", {"message": "Your opponent disconnected."}, to=opponent_sid)
                    del active_games[game_id]

            # Store and start the timer
            disconnect_grace_period[sid] = Timer(5, end_grace_period)
            disconnect_grace_period[sid].start()

            # Notify the opponent
            opponent_sid = game["player2_sid"] if game["player1_sid"] == sid else game["player1_sid"]
            emit("waiting", {"message": "Opponent temporarily disconnected. Waiting..."}, to=opponent_sid)
            return

    # Remove player from the waiting list
    global waiting_players
    waiting_players = [player for player in waiting_players if player["sid"] != sid]


@socketio.on("reconnect")
def handle_reconnect(data):
    """Handle player reconnecting during the grace period."""
    sid = request.sid
    game_id = data.get("game_id")

    if game_id in active_games:
        game = active_games[game_id]

        # Stop the disconnection grace period if it exists
        if sid in disconnect_grace_period:
            disconnect_grace_period[sid].cancel()
            del disconnect_grace_period[sid]

        if sid not in [game["player1_sid"], game["player2_sid"]]:
            emit("error", {"message": "You are not part of this game."})
        else:
            emit("reconnected", {"message": "Reconnected successfully."}, to=sid)


# ----------- GAME LOGIC -----------

@app.route('/play/ai', methods=['POST'])
def play_against_ai():
    """Handle playing against AI."""
    data = request.json
    player_choice = data.get('choice')

    if player_choice not in ['rock', 'paper', 'scissors']:
        return jsonify({"error": "Invalid choice"}), 400

    ai_choice = random.choice(['rock', 'paper', 'scissors'])
    result = determine_ai_winner(player_choice, ai_choice)

    return jsonify({
        "player_choice": player_choice,
        "ai_choice": ai_choice,
        "result": result
    })


def determine_winner(player1_choice, player2_choice):
    """Determine the winner of a multiplayer game."""
    outcomes = {
        "rock": {"rock": "tie", "paper": "Player 2 wins!", "scissors": "Player 1 wins!"},
        "paper": {"rock": "Player 1 wins!", "paper": "tie", "scissors": "Player 2 wins!"},
        "scissors": {"rock": "Player 2 wins!", "paper": "Player 1 wins!", "scissors": "tie"},
    }
    return outcomes[player1_choice][player2_choice]


def determine_ai_winner(player_choice, ai_choice):
    """Determine the winner against AI."""
    outcomes = {
        "rock": {"rock": "tie", "paper": "lose", "scissors": "win"},
        "paper": {"rock": "win", "paper": "tie", "scissors": "lose"},
        "scissors": {"rock": "lose", "paper": "win", "scissors": "tie"},
    }
    return outcomes[player_choice][ai_choice]


# ----------- START THE SERVER -----------
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)