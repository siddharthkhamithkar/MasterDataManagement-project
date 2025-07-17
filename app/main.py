from fastapi import FastAPI
from contextlib import asynccontextmanager 
from app.api.v1.endpoints import entity
from app.core.database import connect_to_mongo, close_mongo_connection, mongodb

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongo()
    print("Mongo Connected:", mongodb.db.name)  # 🔍 Sanity check
    assert mongodb.db is not None, "MongoDB connection failed"
    yield
    close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(entity.router, prefix="/api/v1/entities", tags=["Entities"])

@app.get("/ping", tags=["Health"])
def ping():
    return {"status": "ok"}


