from fastapi import APIRouter, HTTPException
from app.schemas.entity import EntityCreate, EntityOut, EntityIn, EntityUpdate
from app.services.entity import create_entity, list_entities, get_entity_by_id, update_entity, delete_entity, get_entity_by_name
from typing import List

router = APIRouter()

@router.post("/create_entity/", response_model=str)
def add_entity(payload: EntityCreate):
    entity_id = create_entity(payload.dict())
    return entity_id

@router.get("/", response_model=List[EntityOut])
def get_entities():
    return list_entities()

@router.get("/get_entity/id/{entity_id}", response_model=EntityOut)
def read_entity_by_id(entity_id: str):
    entity = get_entity_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.get("/get_entity/name/{entity_name}", response_model=EntityOut)
def read_entity_by_name(entity_name: str):
    entity = get_entity_by_name(entity_name)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.patch("/{entity_id}", response_model=EntityOut)
def update_existing_entity(entity_id: str, entity_data:EntityUpdate):
    success = update_entity(entity_id, entity_data)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found or no changes")
    
    return get_entity_by_id(entity_id)

@router.delete("/delete_entity/{entity_id}")
def delete_existing_entity(entity_id: str):
    success = delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"detail": "Entity deleted"}