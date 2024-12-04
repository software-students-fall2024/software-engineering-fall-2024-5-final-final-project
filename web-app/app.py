""" Flask server for web app - Project 5 """

from flask import Flask, render_template, Blueprint

app = Blueprint('main', __name__)


def create_app():
    test_app = Flask(__name__)
    test_app.register_blueprint(app)

    return test_app

@app.route('/')
def home():
    """Render main page"""
    return render_template('main.html')

# write new functions here



if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0", port=5001, debug=True)


# docker file and docker-compose.yml file in the main dir
# connect the mongodb and chatbot subdirs