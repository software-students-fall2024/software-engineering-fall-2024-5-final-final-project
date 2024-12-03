from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import os
import bcrypt
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)

mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(mongo_uri)
# Setup database for users
db = client['p5_user_database']
users_collection = db['p5_users']
budgets_collection = db['p5_budgets']
expenses_collection = db['p5_expenses']

# Constants
EXPENSE_CATEGORIES = ['Food', 'Transportation', 'Entertainment', 'Housing', 'Grocery', 'Shopping']

# User authentication using session
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    if 'username' in session:
        return redirect('/') 
    return render_template('login.html')

# Login
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = users_collection.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        session['username'] = username 
        return jsonify(message="Login successful!"), 200
    else:
        return jsonify(message="Invalid username or password."), 401

# Signup
@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if users_collection.find_one({'username': username}):
        return jsonify(message="Username already exists."), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    users_collection.insert_one({
        'username': username,
        'email': email,
        'password': hashed_password
    })

    return jsonify(message="Signup successful!"), 201

# Budget
@app.route('/set_budget', methods=['GET', 'POST'])
def set_budget():
    if 'username' not in session:
        return redirect(url_for('auth'))

    if request.method == 'POST':
        try:
            new_amount = float(request.form.get('budget_amount', 0))
            budgets_collection.update_one(
                {'username': session['username']},
                {
                    '$set': {
                        'amount': new_amount,
                        'updated_at': datetime.utcnow()
                    },
                    '$setOnInsert': {
                        'created_at': datetime.utcnow()
                    }
                },
                upsert=True
            )
            return redirect(url_for('set_budget'))
        except ValueError:
            return "Invalid amount", 400

    current_budget = budgets_collection.find_one({'username': session['username']})
    return render_template('set_budget.html', current_budget=current_budget)

# Expense
@app.route('/view_expenses')
def view_expenses():
    if 'username' not in session:
        return redirect(url_for('auth'))
    
    category = request.args.get('category')
    
    # Build query
    query = {'username': session['username']}
    if category:
        query['category'] = category
    
    # Get expenses
    expenses = list(expenses_collection.find(query).sort('date', -1))
    
    # Get current budget
    current_budget = budgets_collection.find_one({'username': session['username']})
    
    return render_template('view_expenses.html', 
                         expenses=expenses,
                         current_budget=current_budget,
                         categories=EXPENSE_CATEGORIES)

@app.route('/edit_expense/<expense_id>', methods=['GET', 'POST'])
def edit_expense(expense_id):
    if 'username' not in session:
        return redirect(url_for('auth'))

    try:
        expense_id = ObjectId(expense_id)
    except:
        return "Invalid expense ID", 400

    if request.method == 'POST':
        try:
            # Validate category
            category = request.form.get('category')
            if category not in EXPENSE_CATEGORIES:
                return "Invalid category", 400

            # Update expense
            expenses_collection.update_one(
                {
                    '_id': expense_id,
                    'username': session['username']
                },
                {
                    '$set': {
                        'amount': float(request.form.get('amount')),
                        'category': category,
                        'date': datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
                        'notes': request.form.get('notes', ''),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return redirect(url_for('view_expenses'))
        except (ValueError, KeyError) as e:
            return str(e), 400
    
    # Get expense for editing
    expense = expenses_collection.find_one({
        '_id': expense_id,
        'username': session['username']
    })
    
    if not expense:
        return "Expense not found", 404
        
    return jsonify({
        'id': str(expense['_id']),
        'amount': expense['amount'],
        'category': expense['category'],
        'date': expense['date'].strftime('%Y-%m-%d'),
        'notes': expense.get('notes', '')
    })

@app.route('/api/expense_data/<date_range>', methods=['GET'])
def get_expense_data(date_range):
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401

    username = session['username']
    start_date, end_date = get_date_range(date_range)

    expenses = list(expenses_collection.find({
        "username": username,
        "date": {"$gte": start_date, "$lt": end_date}
    }, {"_id": 0, "amount": 1}))
    
    data = [expense['amount'] for expense in expenses]
    return jsonify(data)

@app.route('/api/expense_details/<date_range>', methods=['GET'])
def get_expense_details(date_range):
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401

    username = session['username']
    start_date, end_date = get_date_range(date_range)

    pipeline = [
        {
            "$match": {
                "username": username,
                "date": {"$gte": start_date, "$lt": end_date}
            }
        },
        {
            "$group": {
                "_id": "$category",
                "num_transactions": {"$sum": 1},
                "total_amount": {"$sum": "$amount"}
            }
        }
    ]

    result = list(expenses_collection.aggregate(pipeline))
    details = [
        {
            "category": r["_id"],
            "num_transactions": r["num_transactions"],
            "amount_spent": r["total_amount"]
        }
        for r in result
    ]
    return jsonify(details)

def get_date_range(date_range):
    today = datetime.today()
    if date_range == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(weeks=1)
    elif date_range == 'month':
        start_date = today.replace(day=1)
        next_month = (today.month % 12) + 1
        end_date = today.replace(month=next_month, day=1)
    elif date_range == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(year=today.year + 1, month=1, day=1)
    else:
        start_date = end_date = today

    return start_date, end_date

# Helper function to calculate monthly total
def get_monthly_total(username, year, month):
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    pipeline = [
        {
            '$match': {
                'username': username,
                'date': {
                    '$gte': start_date,
                    '$lt': end_date
                }
            }
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$amount'}
            }
        }
    ]
    
    result = list(expenses_collection.aggregate(pipeline))
    return result[0]['total'] if result else 0

if __name__ == '__main__':
    app.run(debug=True)