"""
Authentication related functionality
"""

import logging

from bson import ObjectId

from backend.database import Database, User
from backend import login_manager

db = Database()


logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database by their ID."""
    try:
        return User(db.get_user_by_id(ObjectId(user_id)))
    except Exception as e:
        logger.error(f"Error loading user with ID {user_id}: {e}")
        return None
