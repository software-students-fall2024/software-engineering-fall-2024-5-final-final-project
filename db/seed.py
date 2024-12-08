from pymongo import MongoClient

def seed_database():
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["wishlist_db"]
    db.users.insert_one({"name": "Test User", "username": "testuser"})
    print("Database seeded successfully!")

if __name__ == "__main__":
    seed_database()
