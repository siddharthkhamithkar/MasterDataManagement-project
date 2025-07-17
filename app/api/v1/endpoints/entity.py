from fastapi import APIRouter, HTTPException
from app.schemas.entity import EntityCreate, EntityOut, EntityIn
from app.services.entity import create_entity, list_entities, get_entity_by_id, update_entity, delete_entity
from typing import List

router = APIRouter()

@router.post("/", response_model=str)
def add_entity(payload: EntityCreate):
    entity_id = create_entity(payload.dict())
    return entity_id

@router.get("/", response_model=List[EntityOut])
def get_entities():
    return list_entities()

@router.get("/{entity_id}", response_model=EntityOut)
def read_entity(entity_id: str):
    entity = get_entity_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity

@router.put("/{entity_id}", response_model=EntityOut)
def update_existing_entity(entity_id: str, entity_data: EntityIn):
    updated = update_entity(entity_id, entity_data.dict(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Entity not found")
    return updated

@router.delete("/{entity_id}")
def delete_existing_entity(entity_id: str):
    success = delete_entity(entity_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"detail": "Entity deleted"}