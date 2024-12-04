from flask import Blueprint, jsonify, request, session
from flask_cors import CORS
from database import Database

routes = Blueprint("routes", __name__)
CORS(routes, supports_credentials=True)
db = Database()

@routes.route("/api/login", methods=["POST"])
def login():
    data = request.json
    if data["username"] == "user" and data["password"] == "pw":
        session["username"] = "user"
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid credentials"}), 401

@routes.route("/api/logout", methods=["POST"])
def logout():
    session.pop("username", None)
    return jsonify({"success": True})

@routes.route("/api/user-data")
def get_user_data():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    user_data = db.get_user_data(session["username"])
    return jsonify({
        "budget": user_data["budget"],
        "total_expenses": user_data["total_expenses"],
        "remaining": user_data["budget"] - user_data["total_expenses"]
    })

@routes.route("/api/update-budget", methods=["POST"])
def update_budget():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    db.update_budget(session["username"], float(data["budget"]))
    return jsonify({"success": True})

@routes.route("/api/add-expense", methods=["POST"])
def add_expense():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    db.add_expense(
        session["username"],
        float(data["amount"]),
        data["description"]
    )
    return jsonify({"success": True})

@routes.route("/api/remove-expense", methods=["POST"])
def remove_expense():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    data = request.json
    success = db.remove_expense(session["username"], data["expense_id"])
    return jsonify({"success": success})

@routes.route("/api/expenses")
def get_expenses():
    if "username" not in session:
        return jsonify({"error": "Not authenticated"}), 401
    expenses = db.get_expenses(session["username"])
    return jsonify([{
        "id": str(exp._id),
        "amount": exp.amount,
        "description": exp.description,
        "date": exp.date.isoformat()
    } for exp in expenses])