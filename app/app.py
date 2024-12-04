from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Renders templates/index.html

@app.route('/resume')
def resume():
    return
