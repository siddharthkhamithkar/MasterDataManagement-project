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
    data["created_at"] = datetime.utcnow()
    result = mongodb.db["entities"].insert_one(data)
    return str(result.inserted_id)

def list_entities():
    collection = get_entity_collection()
    entities = []
    for entity in mongodb.db["entities"].find():
        entity["id"] = str(entity["_id"])
        del entity["_id"]
        entities.append(entity)
    return entities

def get_entity_by_id(entity_id: str):
    collection = get_entity_collection()
    entity = collection.find_one({"_id": ObjectId(entity_id)})
    if entity:
        entity["id"] = str(entity["_id"])
        del entity["_id"]
    return entity

def update_entity(entity_id: str, update_data: dict):
    collection = get_entity_collection()
    update_data["updated_at"] = datetime.utcnow()
    updated = collection.find_one_and_update(
        {"_id": ObjectId(entity_id)},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER
    )
    if updated:
        updated["id"] = str(updated["_id"])
        del updated["_id"]
    return updated

def delete_entity(entity_id: str):
    collection = get_entity_collection()
    result = collection.delete_one({"_id": ObjectId(entity_id)})
    return result.deleted_count == 1
