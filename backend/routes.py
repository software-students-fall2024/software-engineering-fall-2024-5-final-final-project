"""
This module defines the API routes for user authentication and financial management.
It handles login, logout, budget updates, expense tracking, and data retrieval.
"""

import logging
from datetime import datetime

from flask import Blueprint, jsonify, request, session
from flask_cors import CORS

from backend.database import Database, MLModel

routes = Blueprint("routes", __name__)
CORS(routes, supports_credentials=True)
db = Database()

logger = logging.getLogger(__name__)


@routes.route("/")
def index():
    """Root route."""
    return jsonify({"status": "ok"}), 200


@routes.route("/api/login", methods=["POST"])
def login():
    """
    Handle user login by validating credentials.
    """
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")

    if username is None or password is None:
        missing_fields = []
        if username is None:
            missing_fields.append("username")
        if password is None:
            missing_fields.append("password")
        return (
            jsonify(
                {
                    "success": False,
                    "message": f"Missing fields: {', '.join(missing_fields)}",
                }
            ),
            400,
        )

    if username == "user" and password == "pw":
        session["username"] = "user"
        logger.info("User %s logged in successfully.", username)
        return jsonify({"success": True})

    logger.warning("Failed login attempt for username: %s", username)
    return jsonify({"success": False, "message": "Invalid credentials"}), 401


@routes.route("/api/logout", methods=["POST"])
def logout():
    """
    Handle user logout by clearing the session.
    """
    username = session.get("username")
    session.pop("username", None)
    logger.info("User %s logged out successfully.", username)
    return jsonify({"success": True})


@routes.route("/api/user-data")
def get_user_data():
    """
    Retrieve user-specific financial data.
    """
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    user_data = db.get_user_data(session["username"])
    return jsonify(
        {
            "budget": user_data.get("budget", 0.0),
            "total_expenses": user_data.get("total_expenses", 0.0),
            "remaining": user_data.get("budget", 0.0)
            - user_data.get("total_expenses", 0.0),
        }
    )


@routes.route("/api/update-budget", methods=["POST"])
def update_budget():
    """
    Update the user's budget.
    """
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json or {}
    budget = data.get("budget")
    if budget is None:
        return jsonify({"success": False, "message": "Missing 'budget' field."}), 400
    try:
        db.update_budget(session["username"], float(budget))
        logger.info("User %s updated budget to %s.", session["username"], budget)
        return jsonify({"success": True})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid budget value."}), 400


@routes.route("/api/add-expense", methods=["POST"])
def add_expense():
    """
    Add a new expense for the user.
    """
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json or {}
    amount = data.get("amount")
    description = data.get("description", "")
    if amount is None:
        return jsonify({"success": False, "message": "Missing 'amount' field."}), 400
    try:
        db.add_expense(session["username"], float(amount), description)
        logger.info(
            "User %s added expense: %s - $%s", session["username"], description, amount
        )
        return jsonify({"success": True})
    except ValueError:
        return jsonify({"success": False, "message": "Invalid amount value."}), 400


@routes.route("/api/remove-expense", methods=["POST"])
def remove_expense():
    """
    Remove an existing expense for the user.
    """
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json or {}
    expense_id = data.get("expense_id")
    if expense_id is None:
        return (
            jsonify({"success": False, "message": "Missing 'expense_id' field."}),
            400,
        )
    success = db.remove_expense(session["username"], expense_id)
    if success:
        logger.info(
            "User %s removed expense with ID %s.", session["username"], expense_id
        )
        return jsonify({"success": True})
    logger.warning(
        "User %s failed to remove expense with ID %s.", session["username"], expense_id
    )
    return jsonify({"success": False, "message": "Expense not found."}), 404


@routes.route("/api/expenses")
def get_expenses():
    """
    Retrieve all expenses for the authenticated user.
    """
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    expenses = db.get_expenses(session["username"])
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
def predict_expenses():
    """
    Predict next month's expenses based on historical data.
    """
    # pylint: disable=too-many-branches
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401

    user_data = db.get_user_data(session["username"])
    expenses = user_data.get("expenses", [])

    if not expenses:
        return jsonify({"error": "No valid expense data available for prediction"}), 400

    # Initialize lists to store months and totals
    months = []
    totals = []

    # Iterate through each expense to extract month and amount
    for expense in expenses:
        # Extract and parse the 'date' field
        if "date" in expense:
            date = expense["date"]
            date_obj = None

            if isinstance(date, str):
                if date.endswith("Z"):
                    date = date[:-1] + "+00:00"
                try:
                    date_obj = datetime.fromisoformat(date)
                except ValueError:
                    logger.error("Invalid date format for expense: %s", expense["date"])
            elif isinstance(date, datetime):
                date_obj = date
            else:
                logger.error("Unsupported date type in expense: %s", expense["date"])

            if date_obj:
                months.append(date_obj.month)
            else:
                logger.error("Skipping expense due to invalid date: %s", expense)
                continue
        else:
            logger.error("Missing 'date' field in expense: %s", expense)
            continue  # Skip this expense due to missing 'date'

        # Extract the 'amount' field
        if "amount" in expense and isinstance(expense["amount"], (int, float)):
            totals.append(expense["amount"])
        else:
            logger.error("Missing or invalid 'amount' field in expense: %s", expense)
            continue  # Skip this expense due to missing or invalid 'amount'

    # Check if we have valid data for prediction
    if not months or not totals:
        return (
            jsonify({"error": "Insufficient valid expense data for prediction."}),
            400,
        )

    # Train the model and predict
    try:
        ml_model = MLModel()
        ml_model.train(months, totals)
        next_month_prediction = ml_model.predict_next_month(max(months))
    except (ValueError, RuntimeError) as e:
        logger.error("Error during expense prediction: %s", e)
        return jsonify({"error": "Failed to predict expenses."}), 500

    # Return the prediction result
    return jsonify({"predicted_expenses": round(next_month_prediction, 2)})
