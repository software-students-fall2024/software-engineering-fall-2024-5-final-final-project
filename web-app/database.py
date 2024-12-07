import os
from pymongo import MongoClient

# MongoDB connection
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/theonepiece")
client = MongoClient(mongo_uri)
db = client.get_default_database()