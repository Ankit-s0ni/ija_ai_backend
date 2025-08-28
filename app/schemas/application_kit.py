from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class ApplicationKitBase(BaseModel):
    resume_id: str
    job_description: str


class ApplicationKitCreate(ApplicationKitBase):
    pass


class ApplicationKitOut(ApplicationKitBase):
    id: str
    user_id: str
    created_at: datetime
    generated_content: Dict[str, Any]

    class Config:
        from_attributes = True
