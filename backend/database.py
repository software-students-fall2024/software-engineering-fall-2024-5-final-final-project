from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

@dataclass
class Expense:
    amount: float
    description: str
    date: datetime
    _id: Optional[ObjectId] = None

class Database:
    def __init__(self, uri="mongodb://mongodb:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client.finance_db
        self._ensure_default_user()

    def _ensure_default_user(self):
        """Ensure default user exists with initial budget"""
        if not self.db.users.find_one({"username": "user"}):
            self.db.users.insert_one({
                "username": "user",
                "password": "pw",
                "budget": 0.0,
                "total_expenses": 0.0
            })

    def get_user_data(self, username: str) -> dict:
        return self.db.users.find_one({"username": username})

    def update_budget(self, username: str, amount: float) -> None:
        try:
            amount = float(amount)
            if not isinstance(amount, (int, float)) or amount < 0:
                raise ValueError("Invalid budget amount")
            
            self.db.users.update_one(
                {"username": username},
                {"$set": {"budget": amount}}
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid budget value: {str(e)}")

    def add_expense(self, username: str, amount: float, description: str) -> None:
        expense = {
            "amount": amount,
            "description": description,
            "date": datetime.utcnow()
        }
        self.db.expenses.insert_one(expense)
        
        # Update total expenses
        self.db.users.update_one(
            {"username": username},
            {"$inc": {"total_expenses": amount}}
        )

    def remove_expense(self, username: str, expense_id: str) -> bool:
        expense = self.db.expenses.find_one({"_id": ObjectId(expense_id)})
        if expense:
            self.db.expenses.delete_one({"_id": ObjectId(expense_id)})
            self.db.users.update_one(
                {"username": username},
                {"$inc": {"total_expenses": -expense["amount"]}}
            )
            return True
        return False

    def get_expenses(self, username: str) -> List[Expense]:
        expenses = self.db.expenses.find().sort("date", -1)
        return [Expense(**exp) for exp in expenses]