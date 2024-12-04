from datetime import datetime
from bson import ObjectId

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        user = User(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password')
        )
        user.created_at = data.get('created_at', datetime.utcnow())
        return user
