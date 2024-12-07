from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()

class User(UserMixin):
    def __init__(self, email, password=None, firstname=None, lastname=None):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.id = email # we'll keep emails as the unique id for users unless we want to change later...
                        # this is not mongodb id so don't get confused

    @staticmethod
    def find_by_email(db, email):
        return db.users.find_one({"email": email})

    @staticmethod
    def create_user(db, email, password, firstname, lastname):
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user_data = {
            "email": email,
            "password": hashed_password,
            "firstname": firstname,
            "lastname": lastname,
        }
        return db.users.insert_one(user_data)

    @staticmethod
    def validate_login(db, email, password):
        user = db.users.find_one({"email": email})
        if user and bcrypt.check_password_hash(user['password'], password):
            return User(
                email=user["email"],
                password=user["password"],
                firstname=user.get("firstname"),
                lastname=user.get("lastname"),
            )
        return None