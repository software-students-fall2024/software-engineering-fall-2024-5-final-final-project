"""
Authentication related functionality
"""

from backend.database import Database, User
from backend import login_manager
from bson import ObjectId

db = Database()


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database by their ID."""
    try:
        return User(db.get_user_by_id(ObjectId(user_id)))
    except:
        return None
