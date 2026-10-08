import os
from pymongo import MongoClient

_client = None

def get_db():
    global _client
    uri = os.environ.get("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI is missing")
    if _client is None:
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client[os.environ.get("MONGODB_DB", "instagram_store")]
