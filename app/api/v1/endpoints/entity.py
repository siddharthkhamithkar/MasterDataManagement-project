from fastapi import APIRouter, HTTPException, Depends
from app.schemas.entity import CustomerCreate, CustomerOut, CustomerIn, CustomerUpdate, CustomerHistoryOut, UserCreate, Token
from app.services.entity import create_entity, list_entities, get_entity_by_id, update_entity, delete_entity, get_entity_history_collection, get_entity_history_by_id, get_entity_by_attribute
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

@router.get("/get_entity/{entity_attribute},{entity_value}", response_model=List[CustomerOut], dependencies=[Depends(verify_token)])
async def read_entity_by_field(entity_attribute: str, entity_value:str):
    try:
        entity = get_entity_by_attribute(entity_attribute, entity_value)
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")