from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from app.schemas.analysis import AnalysisCreate, AnalysisOut
from app.core.database import db
from app.core.security import get_current_user
from app.services.ai_service import analyze_resume_content

router = APIRouter()

def _obj_id(id: str):
    try:
        return ObjectId(id)
    except:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid analysis ID or resume ID")

@router.post("/", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
async def create_analysis(request: AnalysisCreate, current_user=Depends(get_current_user)):
    # Validate resume
    resume = await db.resumes.find_one({"_id": ObjectId(request.resume_id), "user_id": current_user.id})
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    
    # Generate analysis directly
    result = analyze_resume_content(resume.get("resume_data"), request.job_description, request.experience_level)
    
    # Store
    data = {
        "user_id": current_user.id,
        "resume_id": request.resume_id,
        "job_description": request.job_description,
        "experience_level": request.experience_level,
        "score": result.get("score"),
        "keywords_found": result.get("keywords_found"),
        "keywords_missing": result.get("keywords_missing"),
        "created_at": datetime.utcnow()
    }
    res = await db.analyses.insert_one(data)
    data["id"] = str(res.inserted_id)
    return data

@router.get("/", response_model=List[AnalysisOut])
async def list_analyses(current_user=Depends(get_current_user)):
    cursor = db.analyses.find({"user_id": current_user.id})
    analyses = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        analyses.append(doc)
    return analyses

@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(analysis_id: str, current_user=Depends(get_current_user)):
    oid = _obj_id(analysis_id)
    doc = await db.analyses.find_one({"_id": oid, "user_id": current_user.id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    doc["id"] = str(doc["_id"])
    return doc
