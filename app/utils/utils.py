from app.core.database import mongodb
from bson import ObjectId
import copy
from datetime import datetime

def serialize_doc(doc):
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            doc[key] = str(value)
        elif isinstance(value, dict):
            doc[key] = serialize_doc(value)
    return doc

def get_entity_collection():
    if mongodb.db is None:
        raise RuntimeError("Database not initialized. Did you forget to call connect_to_mongo?")
    return mongodb.db["entities"]

def get_entity_history_collection():
    if mongodb.db is None:
        raise RuntimeError("Database not initialized. Did you forget to call connect_to_mongo?")
    return mongodb.db["entity_history"]

async def save_history(entity: dict, operation: str):
    entity_history_collection = get_entity_history_collection()
    history_doc = {
        "entity_id": entity["_id"],
        "version": entity.get("version", 1),
        "data": copy.deepcopy(entity),
        "operation": operation,
        "timestamp": datetime.utcnow()
    }

    entity_history_collection.insert_one(history_doc)