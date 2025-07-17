from app.core.database import mongodb
from bson import ObjectId
from datetime import datetime
from pymongo.collection import ReturnDocument
from app.core.database import mongodb


def get_entity_collection():
    if mongodb.db is None:
        raise RuntimeError("Database not initialized. Did you forget to call connect_to_mongo?")
    return mongodb.db["entities"]


def create_entity(data: dict):
    collection = get_entity_collection()
    data["created_at"] = datetime.utcnow()
    result = collection.insert_one(data)
    return str(result.inserted_id)

def list_entities():
    collection = get_entity_collection()
    entities = []
    for entity in collection.find():
        entity["id"] = str(entity["_id"])
        del entity["_id"]
        entities.append(entity)
    return entities

def get_entity_by_id(entity_id: str):
    collection = get_entity_collection()
    try:
        # Validate that entity_id is a valid ObjectId
        object_id = ObjectId(entity_id)
        entity = collection.find_one({"_id": object_id})
        if entity:
            entity["id"] = str(entity["_id"])
            del entity["_id"]
        return entity
    except Exception:
        # If entity_id is not a valid ObjectId, return None
        return None

def get_entity_by_name(entity_name: str):
    collection = get_entity_collection()
    entity = collection.find_one({"name": entity_name})
    if entity:
        entity["id"] = str(entity["_id"])
        del entity["_id"]
    return entity

def update_entity(entity_id: str, update_data: dict):
    collection = get_entity_collection()
    try:
        # Validate that entity_id is a valid ObjectId
        object_id = ObjectId(entity_id)
        update_data["updated_at"] = datetime.utcnow()
        updated = collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER
        )
        if updated:
            updated["id"] = str(updated["_id"])
            del updated["_id"]
        return updated
    except Exception:
        # If entity_id is not a valid ObjectId, return None
        return None

def delete_entity(entity_id: str):
    collection = get_entity_collection()
    try:
        # Validate that entity_id is a valid ObjectId
        object_id = ObjectId(entity_id)
        result = collection.delete_one({"_id": object_id})
        return result.deleted_count == 1
    except Exception:
        # If entity_id is not a valid ObjectId, return False
        return False
