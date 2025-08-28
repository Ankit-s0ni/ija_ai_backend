from pydantic import BaseModel
from typing import Dict, Optional, List, Any
from datetime import datetime


class PersonalInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class Education(BaseModel):
    degree: str
    school: Optional[str] = None
    year: Optional[str] = None


class Experience(BaseModel):
    title: str
    company: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None


class Project(BaseModel):
    name: str
    technologies: Optional[str] = None
    description: Optional[str] = None


class StructuredResumeData(BaseModel):
    personal_info: PersonalInfo
    education: List[Education] = []
    skills: List[str] = []
    experience: List[Experience] = []
    projects: List[Project] = []


class ResumeBase(BaseModel):
    resume_name: str
    resume_data: Dict


class ResumeCreate(ResumeBase):
    pass


class ResumeCreateFromPDF(BaseModel):
    resume_name: str
    content: str
    personal_info: Optional[PersonalInfo] = None
    education: Optional[List[Education]] = None
    skills: Optional[List[str]] = None
    experience: Optional[List[Experience]] = None
    projects: Optional[List[Project]] = None


class ResumeUpdate(BaseModel):
    resume_name: Optional[str]
    resume_data: Optional[Dict]


class ResumeOut(ResumeBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
