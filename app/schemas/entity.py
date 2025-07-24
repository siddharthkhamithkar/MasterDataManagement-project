from pydantic import BaseModel, Field, validator
from typing import Optional, Any
from bson import ObjectId
from pydantic_core import core_schema
from datetime import datetime

# Custom ObjectId support
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema()
        )

    @classmethod
    def validate(cls, value: Any) -> ObjectId:
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler: Any) -> dict:
        return {"type": "string"}

# Request model for creating an entity
class EntityCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, description="Entity name (3–50 characters)")
    description: Optional[str] = Field(None, max_length=200, description="Optional description")

    @validator("name")
    def name_must_be_alphanumeric(cls, v):
        if not v.replace(" ", "").isalnum():
            raise ValueError("Name must be alphanumeric (spaces allowed)")
        return v

# Request model for updating an entity (PUT)
class EntityIn(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

    @validator("name")
    def name_must_be_alphanumeric(cls, v):
        if v and not v.replace(" ", "").isalnum():
            raise ValueError("Name must be alphanumeric")
        return v

# Update model for PATCH requests
class EntityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=200)

    @validator("name")
    def name_must_be_alphanumeric(cls, v):
        if v and not v.replace(" ", "").isalnum():
            raise ValueError("Name must be alphanumeric")
        return v

    class Config:
        extra = "forbid"  # Reject any unexpected fields

# Response model
class EntityOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    description: Optional[str] = None
    version: Optional[int] = 1  # default to 1 if missing

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class HistoryOut(BaseModel):
    id: str = Field(..., alias="_id")
    entity_id: str
    version: int
    data: dict
    operation: str
    timestamp: datetime

    class Config:
        populate_by_name = True  # allow "id" to populate from "_id"
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str
