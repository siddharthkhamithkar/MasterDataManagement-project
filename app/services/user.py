from app.utils.utils import get_user_collection, hash_password, verify_password
from app.schemas.entity import UserCreate, UserOut
from datetime import datetime
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError
from typing import Optional


async def create_user(user_data: UserCreate) -> str:
    collection = get_user_collection()
    
    # Check if username already exists
    if collection.find_one({"username": user_data.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    if collection.find_one({"email": user_data.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # Hash the password
    hashed_password = hash_password(user_data.password)
    
    # Prepare user document
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "password": hashed_password,
        "full_name": user_data.full_name,
        "created_at": datetime.now(),
        "is_active": True
    }
    
    try:
        # Insert the user
        result = collection.insert_one(user_doc)
        return str(result.inserted_id)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="User with this username or email already exists")


def get_user_by_username(username: str) -> Optional[dict]:
    collection = get_user_collection()
    return collection.find_one({"username": username})


def get_user_by_email(email: str) -> Optional[dict]:
    collection = get_user_collection()
    return collection.find_one({"email": email})


async def authenticate_user(username: str, password: str) -> dict:
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=401, detail="User account is inactive")
    
    return user
