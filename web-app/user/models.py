from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, username, password=None, firstname=None, lastname=None):
        self.username = username
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.id = username # we'll keep emails as the unique id for users unless we want to change later...
                        # this is not mongodb id so don't get confused

    @staticmethod
    def find_by_username(db, username):
        return db.users.find_one({"username": username})

    @staticmethod
    def create_user(db, username, password, firstname, lastname):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_data = {
            "username": username,
            "password": hashed_password,
            "firstname": firstname,
            "lastname": lastname,
        }
        return db.users.insert_one(user_data)

    @staticmethod
    def validate_login(db, username, password):
        user = db.users.find_one({"username": username})
        if user and bcrypt.check_password_hash(user['password'], password):
            return User(
                username=user["username"],
                password=user["password"],
                firstname=user.get("firstname"),
                lastname=user.get("lastname"),
            )
        return None