from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    profile_picture_url: Optional[str] = None


class UserCreate(UserBase):
    google_id: str


class UserOut(UserBase):
    id: str
    google_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserInDB(UserOut):
    pass
