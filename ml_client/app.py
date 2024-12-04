"""
Loads flask app for ml-client
"""

from flask import Flask, request, jsonify, render_template, Blueprint
from helpers.respond import (
    initialize_llm,
    suppress_llama_cpp_logging,
    respond_to_user_input,
)
from helpers.loader import Loader

# Flask app initialization
app = Blueprint("main", __name__)
LOG_CALLBACK = None

# Suppress llama cpp logging
suppress_llama_cpp_logging()


# Initialize the LLM globally
# Ministral-8B-Instruct-2410-Q4_K_M.gguf ./models/Mistral-7B-v0.1.Q3_K_S.gguf
MODEL_PATH = "./models/Ministral-8B-Instruct-2410-Q4_K_M.gguf"
MODEL_PATH = "./models/SmolLM-135M.Q2_K.gguf"
DEFAULT_TEMPERATURE = 0.1

loader = Loader("Initializing large language model...")
loader.start()  # Start the loading spinner

try:
    llm = initialize_llm(MODEL_PATH, DEFAULT_TEMPERATURE)
finally:
    loader.stop()  # Stop the loading spinner when the task completes

def create_app():
    """
    Generate test app
    """
    test_app = Flask(__name__)
    test_app.register_blueprint(app)
    return test_app

@app.route("/")
def index():
    """
    Renders the main page of the application.
    """
    return render_template("index.html")


@app.route("/respond", methods=["POST"])
def handle_user_input():
    """
    Handles POST requests to process user input and return a response.

    Example Use Case:
    curl -X POST http://127.0.0.1:5000/respond \
    -H "Content-Type: application/json" \
    -d '{"user_input": "What is the capital of France?"}'
    """
    try:
        # Extract user input from the request
        data = request.get_json()
        user_input = data.get("user_input", "")

        if not user_input:
            return jsonify({"error": "No user input provided"}), 400

        # Generate response using the LLM
        response = respond_to_user_input(user_input, llm)

        # Return the response as JSON
        return jsonify({"response": response})
    except Exception as e:  # pylint: disable=broad-exception-caught
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002, debug=True)

# docker build -t ml-component .
