"""
Authentication related functionality
"""

import logging

from bson import ObjectId, errors as bson_errors
from pymongo.errors import PyMongoError

from backend.database import Database, User
from backend import login_manager

db = Database()


logger = logging.getLogger(__name__)


@login_manager.user_loader
def load_user(user_id):
    """Load a user from the database by their ID."""
    try:
        return User(db.get_user_by_id(ObjectId(user_id)))
    except bson_errors.InvalidId as e:
        logger.error("Invalid user ID format: %s, %s", user_id, e)
    except PyMongoError as e:
        logger.error("Database error while loading user %s: %s", user_id, e)
    return None
