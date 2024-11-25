from flask import (
    Flask,
    render_template,
    Response,
    request,
    redirect,
    url_for,
    session,
    flash,
)
from pymongo import MongoClient
from datetime import datetime
import cv2
import requests
import os
import bcrypt
import base64
import numpy as np
import time

# Flask configuration
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "test_secret_key")

# MongoDB configuration
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DBNAME = os.getenv("MONGO_DBNAME", "default_db_name")
client = MongoClient(MONGO_URI)
db = client[MONGO_DBNAME]
emotion_data_collection = db["bar"]
users_collection = db["users"]