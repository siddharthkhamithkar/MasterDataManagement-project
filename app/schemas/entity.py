from pydantic import BaseModel, Field, validator, EmailStr
from typing import Optional, Any, List
from typing_extensions import Literal
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

# User models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username (3-50 characters)")
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="Password (minimum 6 characters)")
    full_name: Optional[str] = Field(None, max_length=100, description="Full name of the user")
    
    @validator("username")
    def username_must_be_alphanumeric(cls, v):
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username must be alphanumeric (underscores and hyphens allowed)")
        return v.lower()
    
    @validator("email")
    def validate_email(cls, v):
        if "@" not in v or "." not in v.split("@")[-1]:
            raise ValueError("Invalid email format")
        return v.lower()

class UserOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    email: str
    full_name: Optional[str] = None
    created_at: datetime
    is_active: bool = True
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

#Nested Models

class Address(BaseModel):
    street: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postalCode: Optional[str] = Field(None, max_length=20)
    country: Optional[str] = Field(None, max_length=100)


class PersonalInfo(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=100)
    lastName: str = Field(..., min_length=1, max_length=100)
    dateOfBirth: Optional[datetime]
    gender: Optional[Literal["male", "female", "other", "prefer_not_to_say"]]
    nationality: Optional[str] = Field(None, max_length=100)


class ContactInfo(BaseModel):
    email: Optional[EmailStr]
    phoneNumber: Optional[str] = Field(None, min_length=5, max_length=20)
    address: Optional[Address]


class Preferences(BaseModel):
    language: Optional[str] = Field(None, min_length=2, max_length=10)
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="ISO 4217 code")
    interests: Optional[List[str]] = Field(None, description="List of customer interests")
    communicationChannels: Optional[List[Literal["email", "sms", "push", "phone", "in_person"]]]


class RecentBooking(BaseModel):
    bookingId: str = Field(..., min_length=1, max_length=50)
    date: datetime
    location: str = Field(..., min_length=1, max_length=100)
    serviceType: str = Field(..., min_length=1, max_length=100)


class BehavioralData(BaseModel):
    lastVisitDate: Optional[datetime]
    lifetimeValue: Optional[float] = Field(None, ge=0)
    visitsCount: Optional[int] = Field(None, ge=0)
    averageSpend: Optional[float] = Field(None, ge=0)
    preferredLocation: Optional[str] = Field(None, max_length=100)
    recentBookings: Optional[List[RecentBooking]]


class Consent(BaseModel):
    marketing: Optional[bool] = False
    profiling: Optional[bool] = False
    thirdPartySharing: Optional[bool] = False


class SocialIds(BaseModel):
    facebook: Optional[str] = Field(None, max_length=100)
    instagram: Optional[str] = Field(None, max_length=100)
    twitter: Optional[str] = Field(None, max_length=100)


class ExternalSystemId(BaseModel):
    system: str = Field(..., max_length=100)
    id: str = Field(..., max_length=100)


class Identifiers(BaseModel):
    loyaltyId: Optional[str] = Field(None, max_length=100)
    socialIds: Optional[SocialIds]
    externalSystemIds: Optional[List[ExternalSystemId]]


#Main Customer Models

class CustomerCreate(BaseModel):
    customerId: Optional[str] = None  # server sets this
    personalInfo: PersonalInfo
    contactInfo: ContactInfo
    preferences: Optional[Preferences] = None
    behavioralData: Optional[BehavioralData] = None
    consent: Optional[Consent] = None
    identifiers: Optional[Identifiers] = None

    @validator("customerId")
    def id_must_be_alphanumeric(cls, v):
        if not v.replace("-", "").replace("_", "").isalnum():
            raise ValueError("customerId must be alphanumeric (dashes/underscores allowed)")
        return v


class CustomerIn(BaseModel): 
    personalInfo: Optional[PersonalInfo]
    contactInfo: Optional[ContactInfo]
    preferences: Optional[Preferences]
    behavioralData: Optional[BehavioralData]
    consent: Optional[Consent]
    identifiers: Optional[Identifiers]


class CustomerUpdate(BaseModel): 
    customerId: Optional[str] = None 
    personalInfo: Optional[PersonalInfo] = None
    contactInfo: Optional[ContactInfo] = None
    preferences: Optional[Preferences] = None
    behavioralData: Optional[BehavioralData] = None
    consent: Optional[Consent] = None
    identifiers: Optional[Identifiers] = None

    class Config:
        extra = "forbid" 


class CustomerOut(BaseModel):
    id: str = Field(..., alias="_id")
    customerId: str
    personalInfo: PersonalInfo
    contactInfo: ContactInfo
    preferences: Optional[Preferences]
    behavioralData: Optional[BehavioralData]
    consent: Optional[Consent]
    identifiers: Optional[Identifiers]
    version: Optional[int] = 1

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CustomerHistoryOut(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    customer_id: str
    version: int
    data: dict
    operation: str
    timestamp: datetime

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str} 