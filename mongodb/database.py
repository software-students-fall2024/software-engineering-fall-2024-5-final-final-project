from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

#fetch environment variables
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

#create a mongo client
client = MongoClient(MONGO_URI)
#access the database
db = client[DB_NAME]

#methods

# retrieve all users from the database
def get_users():
    return list(db.users.find())

# add a user to the database
def add_user(user):
    db.users.insert_one(user)

def get_books():
    return list(db.books.find())

# add a book to the database
def add_book(book):
    db.books.insert_one(book)

def get_matches():
    return list(db.matches.find())

# add a match to the database
def add_match(match):
    db.matches.insert_one(match)