""" Flask server for web app - Project 5 """

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    """Render main page"""
    return render_template('main.html')

# write new functions here



if __name__ == '__main__':
    app.run(debug=True, port=8080)