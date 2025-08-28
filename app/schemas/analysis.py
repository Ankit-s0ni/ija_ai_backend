from pydantic import BaseModel
from typing import List
from datetime import datetime


class AnalysisCreate(BaseModel):
    resume_id: str
    job_description: str
    experience_level: str


class AnalysisOut(BaseModel):
    id: str
    user_id: str
    resume_id: str
    job_description: str
    experience_level: str
    score: int
    keywords_found: List[str]
    keywords_missing: List[str]
    created_at: datetime

    class Config:
        from_attributes = True
