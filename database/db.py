import os
from functools import lru_cache

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()


# The original opened a brand-new MongoClient on every call, and get_collection
# was called three times per request. Each client spins up its own connection
# pool and monitor threads, so the app leaked connections under load.
@lru_cache(maxsize=1)
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

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB_NAME]
    return db["predictions"]


def save_prediction(url, result):
    collection = get_collection()
    if collection is None:
        return

    try:
        collection.insert_one({
            "url": url,
            "result": result,
            "timestamp": datetime.now(timezone.utc)
        })
    except PyMongoError:
        # A logging failure must never take down a scan.
        pass


def get_history(limit=10):
    collection = get_collection()
    if collection is None:
        return []

    try:
        return list(
            collection.find().sort("timestamp", -1).limit(limit)
        )
    except PyMongoError:
        return []
