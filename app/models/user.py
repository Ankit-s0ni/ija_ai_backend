from pydantic import BaseModel, EmailStr
from bson import ObjectId
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    full_name: str
    google_id: str
    profile_picture_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        validate_by_name = True
        json_encoders = {ObjectId: str}
