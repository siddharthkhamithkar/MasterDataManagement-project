from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId
from typing import Any
from pydantic_core import core_schema


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
    name: str
    description: Optional[str] = None

# Request model for updating an entity
class EntityIn(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Response model
class EntityOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    description: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }

# Update model for patch requests 
class EntityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    # add more optional fields

    class Config:
        extra = "forbid"  # reject fields not in schema