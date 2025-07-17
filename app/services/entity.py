from app.core.database import mongodb
from bson import ObjectId
from datetime import datetime
from pymongo.collection import ReturnDocument
from pymongo.results import UpdateResult
from app.core.database import mongodb


def get_entity_collection():
    if mongodb.db is None:
        raise RuntimeError("Database not initialized. Did you forget to call connect_to_mongo?")
    return mongodb.db["entities"]


def create_entity(data: dict):
    collection = get_entity_collection()
    data["created_at"] = datetime.now()
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

def update_entity(entity_id: str, entity_data: dict) -> bool:
    collection = mongodb.db["entities"]

    # Remove fields with None (so they are not updated)
    update_data = {k: v for k, v in entity_data.model_dump(exclude_unset=True).items() if v is not None}

    if not update_data:
        return False  # Nothing to update

    result: UpdateResult = collection.update_one(
        {"_id": ObjectId(entity_id)},
        {"$set": update_data}
    )
    return result.modified_count == 1

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
