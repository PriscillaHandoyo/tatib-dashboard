import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

def get_db():
    uri = os.getenv("MONGODB_URI")
    client = MongoClient(uri)
    db = client["tatib"] # db name
    return db
