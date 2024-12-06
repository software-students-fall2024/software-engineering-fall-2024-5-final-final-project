from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/groups')
def groups():
    return render_template('groups.html')

@app.route('/add-expense')
def add_expense():
    return render_template('add-expense.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
