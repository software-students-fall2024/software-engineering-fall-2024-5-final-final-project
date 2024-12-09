from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/?ssl=false")
    print("Connected to MongoDB!")
    print("Databases:", client.list_database_names())
except Exception as e:
    print("Connection failed:", e)