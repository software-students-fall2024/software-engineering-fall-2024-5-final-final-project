import os
import pymongo
from fastapi import FastAPI, HTTPException

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is required")

# Connect to MongoDB
try:
    client = pymongo.MongoClient(MONGO_URI)
    db = client["studySchedulerDB"]
    print("MongoDB connection successful")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Study Scheduler Backend is running"}

@app.get("/users")
def get_users():
    try:
        users = list(db["users"].find({}, {"_id": 0}))
        return {"users": users}
    except Exception as e:
        print(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
