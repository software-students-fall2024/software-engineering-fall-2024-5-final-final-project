import os
from flask import Flask
import pymongo
import gridfs

app = Flask(__name__)

# mongodb
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = pymongo.MongoClient(mongo_uri)
db = client["bookswap"]
fs = gridfs.GridFS(db)
