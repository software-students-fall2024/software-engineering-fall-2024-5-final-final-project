"""
backend.database

This module defines the Database class for managing interactions with a MongoDB backend.
It includes functionality for:
- User authentication
- Budget management
- Expense tracking
- Spending analysis
"""

from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import os
from pymongo import MongoClient
from bson import ObjectId
from flask_login import UserMixin
import bcrypt
from sklearn.linear_model import LinearRegression
import numpy as np


@dataclass
class Expense:
    """
    Represents an individual financial expense with relevant attributes.
    """

    amount: float
    description: str
    date: datetime
    _id: Optional[ObjectId] = None

    @property
    def id(self) -> Optional[str]:
        """Return the string representation of the expense ID."""
        return str(self._id) if self._id else None


class Database:
    """
    Provides methods to interact with the MongoDB database for the finance application.
    Handles user-related operations, budget management, and expense tracking.
    """

    def __init__(self, uri: str = None):
        """
        Initialize the Database instance and ensure the default user exists.
        """
        if uri is None:
            uri = os.environ.get("MONGO_URI", "mongodb://mongodb:27017/")
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client.finance_db
        self._ensure_default_user()

    def _ensure_default_user(self):
        """
        Ensure that the default user exists in the database with an initial budget.
        """
        if not self.db.users.find_one({"username": "user"}):
            hashed_password = bcrypt.hashpw("pw".encode("utf-8"), bcrypt.gensalt())
            self.db.users.insert_one(
                {
                    "username": "user",
                    "password": hashed_password,  # Store hashed password
                    "budget": 0.0,
                    "total_expenses": 0.0,
                }
            )

    def create_user(self, username: str, password: str) -> bool:
        """
        Create a new user with the given username and password.
        Returns True if the user is created successfully, or False if the user already exists.
        """
        existing_user = self.db.users.find_one({"username": username})
        if existing_user:
            return False  # User already exists

        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.db.users.insert_one(
            {
                "username": username,
                "password": hashed_password,
                "budget": 0.0,
                "total_expenses": 0.0,
            }
        )
        return True

    def get_user_data(self, username: str) -> dict:
        """
        Retrieve data for a specific user.
        """
        return self.db.users.find_one({"username": username})

    def get_user_by_id(self, user_id: ObjectId) -> dict:
        """
        Retrieve data with an id.
        """
        return self.db.users.find_one({"_id": user_id})

    def update_budget(self, username: str, amount: float) -> None:
        """
        Update the budget for a specific user.
        """
        try:
            amount = float(amount)
            if not isinstance(amount, (int, float)) or amount < 0:
                raise ValueError("Invalid budget amount")

            self.db.users.update_one(
                {"username": username}, {"$set": {"budget": amount}}
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid budget value: {str(e)}") from e

    def add_expense(self, username: str, amount: float, description: str) -> None:
        """
        Add a new expense for a specific user and update total expenses.
        """
        expense = {
            "username": username,  # Store username for filtering
            "amount": amount,
            "description": description,
            "date": datetime.now(timezone.utc),
        }
        self.db.expenses.insert_one(expense)  # Actually insert the expense

        # Update total expenses for the user
        self.db.users.update_one(
            {"username": username}, {"$inc": {"total_expenses": amount}}
        )

    def remove_expense(self, username: str, expense_id: str) -> bool:
        """
        Remove an existing expense for a specific user.
        """
        expense = self.db.expenses.find_one(
            {"_id": ObjectId(expense_id), "username": username}
        )
        if expense:
            self.db.expenses.delete_one({"_id": ObjectId(expense_id)})
            self.db.users.update_one(
                {"username": username}, {"$inc": {"total_expenses": -expense["amount"]}}
            )
            return True
        return False

    def get_expenses(self, username: str) -> List[Expense]:
        """
        Retrieve all expenses for a specific user.
        """
        expenses = self.db.expenses.find({"username": username}).sort("date", -1)
        expense_list = []

        for exp in expenses:
            expense_data = {
                "amount": exp["amount"],
                "description": exp["description"],
                "date": exp["date"],
                "_id": exp["_id"],
            }
            expense_list.append(Expense(**expense_data))

        return expense_list


class User(UserMixin):
    """
    Represents a user for Flask-Login
    """

    def __init__(self, user_data):
        self.id = str(user_data["_id"])
        self.username = user_data["username"]
        self.password = user_data["password"]

    def get_id(self):
        """Return the ID."""
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True


class MLModel:
    """
    Provides a simple machine learning model to analyze and predict spending habits.
    Uses a linear regression model to find patterns in monthly spending data and make predictions for future months.
    """

    def __init__(self):
        """
        Initialize the model with Linear Regression.
        """
        self.model = LinearRegression()

    def train(self, months, expenses):
        """
        Reshape data for training (sklearn expects 2D array for X)
        Args:
            months (List[int]): A list of months (numerical representation)
            expenses (List[float]): A list of total expenses for each month
        """
        x = np.array(months).reshape(-1, 1)
        y = np.array(expenses)
        self.model.fit(x, y)

    def predict_next_month(self, current_month):
        """
        Predict for the next month using the trained linear regression model
        Args:
            current_month (int): The numerical representation of the current month
        Returns:
            float: The predicted expense value for the next month.
        """
        next_month = np.array([[current_month + 1]])
        return self.model.predict(next_month)[0]
