# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    MONGO_DB: str

    class Config:
        env_file = ".env"

settings = Settings()
