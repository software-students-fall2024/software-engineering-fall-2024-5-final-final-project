"""
backend.routes

This module defines the API routes for user authentication and financial management.
It handles login, logout, budget updates, expense tracking, and data retrieval.
"""

from flask import Blueprint, jsonify, request
from flask_cors import CORS
from flask_login import login_user, logout_user, login_required, current_user
import bcrypt
from backend.database import Database, User  # pylint: disable=import-error

routes = Blueprint("routes", __name__)
CORS(routes, supports_credentials=True)
db = Database()


@routes.route("/")
def index():
    """Root route."""
    return jsonify({"status": "ok"}), 200


@routes.route("/api/login", methods=["POST"])
def login():
    """
    Handle user login by validating credentials.
    """
    data = request.json

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400

    user_data = db.get_user_data(data["username"])

    if user_data and bcrypt.checkpw(
        data["password"].encode("utf-8"), user_data["password"]
    ):
        user = User(user_data)
        login_user(user)  # Log the user in
        return jsonify({"success": True})

    return jsonify({"success": False, "message": "Invalid credentials"}), 401


@routes.route("/api/logout", methods=["POST"])
@login_required
def logout():
    """
    Handle user logout.
    """
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})


@routes.route("/api/user-data")
@login_required
def get_user_data():
    """
    Retrieve user-specific financial data.
    """
    user_data = db.get_user_data(current_user.username)
    return jsonify(
        {
            "budget": user_data["budget"],
            "total_expenses": user_data["total_expenses"],
            "remaining": user_data["budget"] - user_data["total_expenses"],
        }
    )


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
    db.add_expense(current_user.get_id(), float(data["amount"]), data["description"])
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
