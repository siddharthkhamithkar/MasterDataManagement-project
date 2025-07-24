from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager 
from app.api.v1.endpoints import entity, token
from app.core.database import connect_to_mongo, close_mongo_connection, mongodb
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.utils import get_openapi

@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_to_mongo()
    print("Mongo Connected:", mongodb.db.name)  # Sanity check
    assert mongodb.db is not None, "MongoDB connection failed"
    yield
    close_mongo_connection()

app = FastAPI(lifespan=lifespan)

app.include_router(token.router, prefix="/api/v1", tags=["Auth"])
app.include_router(entity.router, prefix="/api/v1/entities", tags=["Entities"])

@app.get("/ping", tags=["Health"])
def ping():
    return {"status": "ok"}

bearer_scheme = HTTPBearer()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="MDM API",
        version="1.0.0",
        description="API for MDM platform",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer"
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"HTTPBearer": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi