from pymongo import MongoClient
# temporary place holder
def seed_database():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["wishlist_db"]
    db.users.insert_one({"name": "Test User"})
    print("Database seeded!")

if __name__ == "__main__":
    seed_database()
