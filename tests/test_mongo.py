from pymongo import MongoClient

def test_connection():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        print("Connected to MongoDB!")
        print("Databases:", client.list_database_names())
    except Exception as e:
        print("Error connecting to MongoDB:", e)

if __name__ == "__main__":
    test_connection()