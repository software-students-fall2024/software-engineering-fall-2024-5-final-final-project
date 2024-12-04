import os
import pymongo
from fastapi import FastAPI, HTTPException
from flask import Flask, render_template
from calendar import Calendar, month_name
import datetime

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


app = Flask(__name__)


@app.route("/")
@app.route("/calendar/<int:month>/<int:year>")
def calendar(month=None, year=None):
    today = datetime.date.today()
    month = month or today.month
    year = year or today.year

    cal = Calendar().monthdayscalendar(year, month)
    days_of_week = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    prev_month = (month - 1) if month > 1 else 12
    next_month = (month + 1) if month < 12 else 1
    prev_year = year if month > 1 else year - 1
    next_year = year if month < 12 else year + 1

    return render_template(
        "index.html",
        calendar_days=cal,
        days_of_week=days_of_week,
        month_name=month_name[month],
        year=year,
        prev_month=prev_month,
        prev_year=prev_year,
        next_month=next_month,
        next_year=next_year,
    )
