import os
from flask import Flask
import pymongo
import gridfs

app = Flask(__name__)

# mongodb
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME")
client = pymongo.MongoClient(mongo_uri)
db = client[db_name]
fs = gridfs.GridFS(db)