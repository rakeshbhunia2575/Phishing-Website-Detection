import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def get_collection():
    MONGO_USERNAME = os.getenv("MONGO_USERNAME")
    MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
    MONGO_CLUSTER = os.getenv("MONGO_CLUSTER")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

    if not all([MONGO_USERNAME, MONGO_PASSWORD, MONGO_CLUSTER, MONGO_DB_NAME]):
        print("MongoDB env vars not found — skipping DB connection")
        return None

    uri = (
        f"mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}"
        f"@{MONGO_CLUSTER}/{MONGO_DB_NAME}"
        "?retryWrites=true&w=majority"
    )

    client = MongoClient(uri)
    db = client[MONGO_DB_NAME]
    return db["predictions"]


def save_prediction(url, result):
    collection = get_collection()
    if collection is None:
        return

    collection.insert_one({
        "url": url,
        "result": result,
        "timestamp": datetime.utcnow()
    })


def get_history(limit=10):
    collection = get_collection()
    if collection is None:
        return []

    return list(
        collection.find()
        .sort("timestamp", -1)   
        .limit(limit)
    )
