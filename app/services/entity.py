from app.core.database import mongodb
from bson import ObjectId
from datetime import datetime
from app.schemas.entity import CustomerUpdate, CustomerHistoryOut
from fastapi import HTTPException
from app.utils.utils import serialize_doc, get_entity_collection, get_entity_history_collection, save_history

async def create_entity(data: dict):
    collection = get_entity_collection()
    object_id = ObjectId()
    data["_id"] = object_id
    data["customerId"] = str(object_id)

    data["created_at"] = datetime.utcnow()

    result = collection.insert_one(data)
    await save_history(data, "create")
    return str(result.inserted_id)

def list_entities():
    collection = get_entity_collection()
    entities = []
    for entity in collection.find():
        entity["id"] = str(entity["_id"])
        del entity["_id"]
        entities.append(entity)
    return entities

def get_entity_by_id(entity_id: str):
    collection = get_entity_collection()
    try:
        object_id = ObjectId(entity_id)
        entity = collection.find_one({"_id": object_id})
        if entity:
            entity["id"] = str(entity["_id"])
            del entity["_id"]
        return entity
    except Exception:
        return None

async def update_entity(entity_id: str, update_data: CustomerUpdate):
    collection = get_entity_collection()
    existing = collection.find_one({"_id": ObjectId(entity_id)})
    if not existing:
        raise HTTPException(status_code=404, detail="Entity not found")

    new_version = existing.get("version", 1) + 1
    update_doc = update_data.model_dump(exclude_unset=True)
    update_doc["version"] = new_version
    updated_entity = {**existing, **update_doc}
    await save_history(updated_entity, operation="update")

    collection.update_one(
        {"_id": ObjectId(entity_id)},
        {"$set": update_doc}
    )

    updated = collection.find_one({"_id": ObjectId(entity_id)})
    return updated

async def delete_entity(entity_id: str):
    collection = get_entity_collection()
    collection_history = get_entity_history_collection()
    try:
        object_id = ObjectId(entity_id)
        entity = collection.find_one({"_id": object_id})
        entity_history = collection_history.find_one({"entity_id": object_id})
        if not entity and not entity_history:
            return False
        try:
            collection.delete_one({"_id": object_id})
            collection_history.delete_one({"entity_id": object_id})
            deletion_successful = True
        except Exception:
            deletion_successful = False
        if deletion_successful:
            return True
        return False
        

    except Exception:
        return False

def get_entity_history_by_id(entity_id: str) -> list[CustomerHistoryOut]:
    history_collection = get_entity_history_collection()
    object_id = ObjectId(entity_id)

    cursor = history_collection.find({"entity_id": object_id}).sort("version", 1)

    history = []
    for doc in cursor:
        doc = serialize_doc(doc)

        history.append(CustomerHistoryOut(**doc))

    return history

def get_entity_by_attribute(entity_attribute: str, entity_value: str):
    ALLOWED_FIELDS = {
    "customerId",
    "personalInfo.firstName",
    "personalInfo.lastName",
    "personalInfo.dateOfBirth",
    "personalInfo.gender",
    "personalInfo.nationality",
    "contactInfo.email",
    "contactInfo.countryCode",
    "contactInfo.phoneNumber",
    "contactInfo.address.street",
    "contactInfo.address.city",
    "contactInfo.address.state",
    "contactInfo.address.postalCode",
    "contactInfo.address.country",
    "preferences.language",
    "preferences.currency",
    "preferences.interests",
    "preferences.communicationChannels",
    "behavioralData.lastVisitDate",
    "behavioralData.lifetimeValue",
    "behavioralData.visitsCount",
    "behavioralData.averageSpend",
    "behavioralData.preferredLocation",
    "behavioralData.recentBookings.bookingId",
    "behavioralData.recentBookings.date",
    "behavioralData.recentBookings.location",
    "behavioralData.recentBookings.serviceType",
    "consent.marketing",
    "consent.profiling",
    "consent.thirdPartySharing",
    "identifiers.loyaltyId",
    "identifiers.socialIds.facebook",
    "identifiers.socialIds.instagram",
    "identifiers.socialIds.twitter",
    "identifiers.externalSystemIds.system",
    "identifiers.externalSystemIds.id",
    }

    collection = get_entity_collection()

    if entity_attribute not in ALLOWED_FIELDS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid search field '{entity_attribute}'."
        )

    query = {entity_attribute: entity_value}
    cursor = collection.find(query)

    results = []
    for entity in cursor:
        entity["id"] = str(entity["_id"])
        del entity["_id"]
        results.append(entity)

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"No entity found for {entity_attribute}={entity_value}"
        )

    return results