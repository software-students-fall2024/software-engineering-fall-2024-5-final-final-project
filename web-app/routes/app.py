from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from uuid import uuid4
import random

# Initialize app and SocketIO
app = Flask(__name__, template_folder="../templates", static_folder="../static")
app.secret_key = "your_secret_key"
socketio = SocketIO(app, manage_session=True)

# In-memory data
player_stats = {"wins": 0, "losses": 0, "ties": 0}
active_games = {}
waiting_players = []

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
    """Handle the game logic for playing against AI."""
    data = request.json
    player_name = data.get('player_name', 'Player')
    player_choice = data.get('choice')

    if player_choice not in ['rock', 'paper', 'scissors']:
        return jsonify({"error": "Invalid choice"}), 400

    ai_choice = random.choice(['rock', 'paper', 'scissors'])
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
    """Determine the winner for AI games."""
    outcomes = {
        "rock": {"rock": "tie", "paper": "lose", "scissors": "win"},
        "paper": {"rock": "win", "paper": "tie", "scissors": "lose"},
        "scissors": {"rock": "lose", "paper": "win", "scissors": "tie"}
    }
    return outcomes[player_choice][ai_choice]

def update_player_stats(result):
    """Update the player's stats based on the result of the game."""
    if result == 'win':
        player_stats['wins'] += 1
    elif result == 'lose':
        player_stats['losses'] += 1
    elif result == 'tie':
        player_stats['ties'] += 1

@app.route('/create-game', methods=['POST'])
def create_game():
    """Create a new game session for inviting a friend."""
    try:
        game_id = str(uuid4())
        active_games[game_id] = {
            "player1": None,
            "player2": None,
            "player1_choice": None,
            "player2_choice": None,
            "result": None
        }
        invite_link = f"http://127.0.0.1:5000/real_person?gameId={game_id}"
        print(f"Game created with ID: {game_id}")
        return jsonify({"game_id": game_id, "invite_link": invite_link})
    except Exception as e:
        print(f"Error in /create-game: {e}")
        return jsonify({"error": "Failed to create game."}), 500

# ----------- MATCHMAKING -----------
@app.route('/random-match', methods=['POST'])
def random_match():
    """Match players randomly."""
    player_name = request.json.get("player_name")
    if not player_name:
        return jsonify({"error": "Player name is required"}), 400

    if waiting_players:
        opponent = waiting_players.pop(0)
        game_id = str(uuid4())
        active_games[game_id] = {
            "player1": opponent,
            "player2": player_name,
            "player1_choice": None,
            "player2_choice": None,
            "result": None
        }
        return jsonify({"status": "matched", "game_id": game_id, "opponent": opponent})
    else:
        waiting_players.append(player_name)
        return jsonify({"status": "waiting"})

@app.route('/cancel-waiting', methods=['POST'])
def cancel_waiting():
    """Cancel the waiting state."""
    player_name = request.json.get("player_name")
    if player_name in waiting_players:
        waiting_players.remove(player_name)
        return jsonify({"status": "canceled"})
    return jsonify({"error": "Player not in waiting list."}), 404

@app.route('/submit-choice', methods=['POST'])
def submit_choice():
    """Submit a player's choice."""
    data = request.json
    game_id = data.get("game_id")
    player_name = data.get("player_name")
    choice = data.get("choice")

    if game_id not in active_games:
        return jsonify({"error": "Invalid game ID."}), 400

    game = active_games[game_id]
    if player_name == game["player1"]:
        game["player1_choice"] = choice
    elif player_name == game["player2"]:
        game["player2_choice"] = choice

    if game["player1_choice"] and game["player2_choice"]:
        result = determine_winner(game["player1_choice"], game["player2_choice"])
        game["result"] = result
        return jsonify({"result": result})
    return jsonify({"status": "waiting for opponent choice"})

def determine_winner(player1_choice, player2_choice):
    """Determine the winner based on player choices."""
    outcomes = {
        "rock": {"rock": "tie", "paper": "Player 2 wins!", "scissors": "Player 1 wins!"},
        "paper": {"rock": "Player 1 wins!", "paper": "tie", "scissors": "Player 2 wins!"},
        "scissors": {"rock": "Player 2 wins!", "paper": "Player 1 wins!", "scissors": "tie"}
    }
    return outcomes[player1_choice][player2_choice]

# ----------- SOCKETIO HANDLERS -----------

@socketio.on("disconnect")
def handle_disconnect():
    """Handle player disconnection."""
    player_name = session.get("player_name")
    if player_name in waiting_players:
        waiting_players.remove(player_name)
        print(f"{player_name} disconnected and removed from waiting list.")

# ----------- START THE SERVER -----------
if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
