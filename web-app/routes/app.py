from flask import Flask, render_template, request, jsonify
from uuid import uuid4
import random

app = Flask(__name__, template_folder="../templates", static_folder="../static")

player_stats = {"wins": 0, "losses": 0, "ties": 0} 
active_games = {} 
waiting_players = [] 

@app.route('/')
def home():
    """
    Render the home page.
    """
    return render_template('home.html')

@app.route('/ai')
def ai_page():
    """
    Render the AI game page.
    """
    return render_template('ai.html')

@app.route('/play/ai', methods=['POST'])
def play_against_ai():
    """
    Handle the game logic for playing against AI.
    """
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
    """
    Determine the winner for AI games.
    """
    outcomes = {
        "rock": {"rock": "tie", "paper": "lose", "scissors": "win"},
        "paper": {"rock": "win", "paper": "tie", "scissors": "lose"},
        "scissors": {"rock": "lose", "paper": "win", "scissors": "tie"}
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

@app.route('/create-game', methods=['POST'])
def create_game():
    """
    Create a new game session for inviting a friend.
    """
    game_id = str(uuid4())
    active_games[game_id] = {
        "player1": None,
        "player2": None,
        "player1_choice": None,
        "player2_choice": None,
        "result": None
    }
    return jsonify({"game_id": game_id, "invite_link": f"http://127.0.0.1:5004/real_person.html?gameId={game_id}"})

@app.route('/random-match', methods=['POST'])
def random_match():
    """
    Match the player with a random opponent.
    """
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

@app.route('/submit-choice', methods=['POST'])
def submit_choice():
    """
    Submit a player's choice for the game.
    """
    data = request.json
    game_id = data.get("game_id")
    player = data.get("player") 
    choice = data.get("choice")

    if game_id not in active_games:
        return jsonify({"error": "Invalid game ID"}), 400

    game = active_games[game_id]
    if player == "player1":
        game["player1_choice"] = choice
    elif player == "player2":
        game["player2_choice"] = choice

    if game["player1_choice"] is not None and game["player2_choice"] is not None:
        result = determine_winner(game["player1_choice"], game["player2_choice"])
        game["result"] = result

    return jsonify({
        "status": "choice recorded",
        "result": game.get("result"),
        "player1_choice": game.get("player1_choice"),
        "player2_choice": game.get("player2_choice")
    })

@app.route('/get-result/<game_id>', methods=['GET'])
def get_result(game_id):
    """
    Retrieve the result of a game.
    """
    if game_id not in active_games:
        return jsonify({"error": "Invalid game ID"}), 400

    game = active_games[game_id]
    return jsonify({
        "player1_choice": game["player1_choice"],
        "player2_choice": game["player2_choice"],
        "result": game["result"]
    })

def determine_winner(player1_choice, player2_choice):
    """
    Determine the winner based on player choices.
    """
    outcomes = {
        "rock": {"rock": "tie", "paper": "Player 2 wins!", "scissors": "Player 1 wins!"},
        "paper": {"rock": "Player 1 wins!", "paper": "tie", "scissors": "Player 2 wins!"},
        "scissors": {"rock": "Player 2 wins!", "paper": "Player 1 wins!", "scissors": "tie"}
    }

    if player1_choice is None and player2_choice is None:
        return "tie"
    elif player1_choice is None:
        return "Player 2 wins!"
    elif player2_choice is None:
        return "Player 1 wins!"
    else:
        return outcomes[player1_choice][player2_choice]

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)