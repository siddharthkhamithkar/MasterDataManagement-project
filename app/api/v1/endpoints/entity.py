from fastapi import APIRouter, HTTPException, Depends
from app.schemas.entity import CustomerCreate, CustomerOut, CustomerIn, CustomerUpdate, CustomerHistoryOut, UserCreate, Token
from app.services.entity import create_entity, list_entities, get_entity_by_id, update_entity, delete_entity, get_entity_by_name, get_entity_history_collection, get_entity_history_by_id

from typing import List
from app.api.v1.endpoints.token import verify_token
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.config import settings

router = APIRouter()


@router.post("/create_entity/", response_model=str, dependencies=[Depends(verify_token)])
async def add_entity(payload: CustomerCreate):
    try:
        entity_id = await create_entity(payload.dict())
        return entity_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/", response_model=List[CustomerOut], dependencies=[Depends(verify_token)])
async def get_entities():
    try:
        return list_entities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/get_entity/id/{entity_id}", response_model=CustomerOut, dependencies=[Depends(verify_token)])
def read_entity_by_id(entity_id: str):
    try:
        entity = get_entity_by_id(entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/get_entity/name/{entity_name}", response_model=List[CustomerOut], dependencies=[Depends(verify_token)])
async def read_entity_by_name(entity_name: str):
    try:
        entity = get_entity_by_name(entity_name)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.patch("/{entity_id}", response_model=CustomerOut, dependencies=[Depends(verify_token)])
async def update_existing_entity(entity_id: str, entity_data:CustomerUpdate):
    try:
        success = await update_entity(entity_id, entity_data)
        if not success:
            raise HTTPException(status_code=404, detail="Entity not found or no changes")
        return get_entity_by_id(entity_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.delete("/delete_entity/{entity_id}", dependencies=[Depends(verify_token)])
async def delete_existing_entity(entity_id: str):
    try:
        success = await delete_entity(entity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Entity not found")
        return {"detail": "Entity deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/entities/{entity_id}/history", response_model=list[CustomerHistoryOut], dependencies=[Depends(verify_token)])
async def get_entity_history(entity_id: str):
    try:
        history = get_entity_history_by_id(entity_id)
        if not history:
            raise HTTPException(status_code=404, detail="No history found for this entity")
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

from app.core.database import mongodb
from bson import ObjectId
from datetime import datetime
from app.schemas.entity import CustomerUpdate, CustomerHistoryOut
from fastapi import HTTPException
from app.utils.utils import serialize_doc, get_entity_collection, get_entity_history_collection, save_history


async def create_entity(data: dict):
    collection = get_entity_collection()

    # Generate ObjectId
    object_id = ObjectId()
    data["_id"] = object_id
    data["customerId"] = str(object_id)

    data["created_at"] = datetime.utcnow()

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

async def update_entity(entity_id: str, update_data: CustomerUpdate):
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

def get_entity_history_by_id(entity_id: str) -> list[CustomerHistoryOut]:
    history_collection = get_entity_history_collection()
    object_id = ObjectId(entity_id)

    cursor = history_collection.find({"entity_id": object_id}).sort("version", 1)

    history = []
    for doc in cursor:
        doc = serialize_doc(doc)

        history.append(CustomerHistoryOut(**doc))

    return history

#TODO: create endpoint to search through any of the available attributes, as a replacement for get_entity_by_name