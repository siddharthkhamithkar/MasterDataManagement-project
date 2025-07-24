# app/core/database.py

from pymongo import MongoClient
from app.core.config import settings


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        print("[MongoDB] Connected to DB:", self.db.name)

    def close(self):
        if self.client:
            self.client.close()

mongodb = MongoDB()

def connect_to_mongo():
    mongodb.connect()

def close_mongo_connection():
    mongodb.close()
