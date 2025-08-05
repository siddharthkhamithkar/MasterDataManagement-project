from app.core.database import mongodb
from bson import ObjectId
from datetime import datetime, timedelta
from pymongo.collection import ReturnDocument
from pymongo.results import UpdateResult
from app.core.database import mongodb
from app.schemas.entity import EntityUpdate
from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
import copy
from app.utils.utils import serialize_doc

def get_entity_collection():
    if mongodb.db is None:
        raise RuntimeError("Database not initialized. Did you forget to call connect_to_mongo?")
    return mongodb.db["entities"]

def get_entity_history_collection():
    if mongodb.db is None:
        raise RuntimeError("Database not initialized. Did you forget to call connect_to_mongo?")
    return mongodb.db["entity_history"]

async def create_entity(data: dict):
    collection = get_entity_collection()
    data["created_at"] = datetime.now()
    result = collection.insert_one(data)
    await save_history(data, "create")
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
        object_id = ObjectId(entity_id)
        entity = collection.find_one({"_id": object_id})
        if entity:
            entity["id"] = str(entity["_id"])
            del entity["_id"]
        return entity
    except Exception:
        return None

def get_entity_by_name(entity_name: str):
    collection = get_entity_collection()
    entities = []
    for entity in collection.find():
        if entity.get("name") == entity_name:
            entity["id"] = str(entity["_id"])
            del entity["_id"]
            entities.append(entity)
    if not entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entities

async def update_entity(entity_id: str, update_data: EntityUpdate):
    collection = get_entity_collection()
    existing = collection.find_one({"_id": ObjectId(entity_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Entity not found")

    new_version = existing.get("version", 1) + 1
    update_doc = update_data.model_dump(exclude_unset=True)
    update_doc["version"] = new_version
    updated_entity = {**existing, **update_doc}
    await save_history(updated_entity, operation="update")

    collection.update_one(
        {"_id": ObjectId(entity_id)},
        {"$set": update_doc}
    )

    updated = collection.find_one({"_id": ObjectId(entity_id)})
    return updated

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


async def delete_entity(entity_id: str):
    collection = get_entity_collection()
    try:
        object_id = ObjectId(entity_id)
        entity = collection.find_one({"_id": object_id})
        if not entity:
            return False
        result = collection.delete_one({"_id": object_id})
        if result.deleted_count == 1:
            await save_history(entity, "delete")
            return True
        return False

    except Exception:
        return False

def get_entity_history_by_id(entity_id: str):
    history_collection = get_entity_history_collection()
    object_id = ObjectId(entity_id)
    cursor = history_collection.find({"entity_id": object_id}).sort("version", 1)
    history = [serialize_doc(doc) for doc in cursor]
    return history
