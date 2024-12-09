from flask import Blueprint, jsonify, request, session
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt
import logging
from backend.database import Database, MLModel, User
from backend.auth import db

logging.basicConfig(level=logging.INFO)

routes = Blueprint("routes", __name__)
CORS(routes, supports_credentials=True)

@routes.route("/")
def index():
    """Root route."""
    return jsonify({"status": "ok"}), 200

@routes.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user_data = db.get_user_data(data["username"])
    
    if user_data and bcrypt.checkpw(
        data["password"].encode("utf-8"), user_data["password"]
    ):
        user = User(user_data)
        login_user(user)
        logging.info(f"User {user.username} logged in successfully.")
        return jsonify({"success": True})
        
    logging.warning(f"Failed login attempt for username: {data['username']}")
    return jsonify({"success": False}), 401

@routes.route("/api/logout", methods=["POST"])
@login_required
def logout():
    """
    Handle user logout.
    """
    username = current_user.username
    logout_user()
    response = jsonify({"success": True, "message": "Logged out successfully"})
    # Delete the 'session' cookie
    response.delete_cookie('session', path='/')
    logging.info(f"User {username} logged out successfully.")
    return response

@routes.route("/api/user-data")
@login_required
def get_user_data():
    """Retrieve user-specific financial data."""
    if not current_user.is_authenticated:
        return jsonify({"error": "Not authenticated"}), 401
        
    user_data = db.get_user_data(current_user.username)
    return jsonify({
        "budget": user_data["budget"],
        "total_expenses": user_data["total_expenses"],
        "remaining": user_data["budget"] - user_data["total_expenses"],
    })

@routes.route("/api/update-budget", methods=["POST"])
@login_required
def update_budget():
    """
    Update the user's budget.
    """
    data = request.json
    db.update_budget(current_user.username, float(data["budget"]))
    return jsonify({"success": True})

@routes.route("/api/add-expense", methods=["POST"])
@login_required
def add_expense():
    """
    Add a new expense for the user.
    """
    data = request.json
    db.add_expense(current_user.username, float(data["amount"]), data["description"])
    return jsonify({"success": True})

@routes.route("/api/remove-expense", methods=["POST"])
@login_required
def remove_expense():
    """
    Remove an existing expense for the user.
    """
    data = request.json
    success = db.remove_expense(current_user.username, data["expense_id"])
    return jsonify({"success": success})

@routes.route("/api/expenses")
@login_required
def get_expenses():
    """
    Retrieve all expenses for the authenticated user.
    """
    expenses = db.get_expenses(current_user.username)
    return jsonify(
        [
            {
                "id": str(exp.id),  # Changed to use 'id' instead of '_id'
                "amount": exp.amount,
                "description": exp.description,
                "date": exp.date.isoformat(),
            }
            for exp in expenses
        ]
    )

@routes.route("/api/predict-expenses", methods=["GET"])
@login_required
def predict_expenses():
    """
    Predict next month's expenses based on historical data.
    """
    # Fetch all user's current expenses
    expenses = db.get_expenses(current_user.username)

    if not expenses or all(exp.amount <= 0 for exp in expenses):
        return jsonify({"error": "No valid expense data available for prediction"}), 400

    # Get the data for training
    months = [expense.date.month for expense in expenses]
    totals = [expense.amount for expense in expenses]

    # Train the model and make predictions
    ml_model = MLModel()
    ml_model.train(months, totals)
    next_month_prediction = ml_model.predict_next_month(max(months))

    return jsonify({"predicted_expenses": round(next_month_prediction, 2)})
