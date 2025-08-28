from typing import Optional
from datetime import datetime, timedelta
from bson import ObjectId

from app.core.database import db
from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    try:
        oid = ObjectId(user_id)
        doc = await db.users.find_one({"_id": oid})
        if doc:
            doc["id"] = str(doc["_id"])
            return User(**doc)
        return None
    except Exception:
        return None


async def get_user_by_google_id(google_id: str) -> Optional[User]:
    """Get user by Google ID"""
    doc = await db.users.find_one({"google_id": google_id})
    if doc:
        doc["id"] = str(doc["_id"])
        return User(**doc)
    return None


async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    doc = await db.users.find_one({"email": email})
    if doc:
        doc["id"] = str(doc["_id"])
        return User(**doc)
    return None


async def create_user(user_data: UserCreate) -> User:
    """Create a new user"""
    now = datetime.utcnow()
    doc = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "google_id": user_data.google_id,
        "profile_picture_url": user_data.profile_picture_url,
        "created_at": now,
        "updated_at": now
    }
    result = await db.users.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    return User(**doc)


async def update_user(user_id: str, updates: dict) -> Optional[User]:
    """Update user information"""
    try:
        oid = ObjectId(user_id)
        updates["updated_at"] = datetime.utcnow()
        result = await db.users.update_one({"_id": oid}, {"$set": updates})
        if result.modified_count > 0:
            return await get_user_by_id(user_id)
        return None
    except Exception:
        return None
