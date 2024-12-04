from flask import Flask, render_template, Blueprint, request, jsonify
import logging

app = Blueprint('main', __name__)

# logging for dev -- delete later
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def create_app():
    test_app = Flask(__name__)
    test_app.register_blueprint(app)
    return test_app

@app.route('/')
def home():
    return render_template('main.html')

@app.route('/call_model', methods=['POST'])
def call_model():
    user_input = request.form['user_input']
    logging.info(f"Input: {user_input}")
    return jsonify({"response": "call to call_model successful"})

if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)