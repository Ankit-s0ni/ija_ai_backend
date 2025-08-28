from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from bson import ObjectId

from app.schemas.application_kit import ApplicationKitCreate, ApplicationKitOut
from app.core.database import db
from app.core.security import get_current_user
from app.services.ai_service import generate_application_kit_content, generate_application_kit_content_chain

router = APIRouter()


def _obj_id(id: str):
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid kit ID")


@router.post("/", response_model=ApplicationKitOut, status_code=status.HTTP_201_CREATED)
async def create_kit(kit: ApplicationKitCreate, current_user=Depends(get_current_user)):
    # Fetch resume
    resume = await db.resumes.find_one({"_id": ObjectId(kit.resume_id), "user_id": current_user.id})
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    
    # Generate content directly (original implementation)
    generated_content = generate_application_kit_content(resume.get("resume_data"), kit.job_description)
    
    # Store in DB
    data = {
        "user_id": current_user.id,
        "resume_id": kit.resume_id,
        "job_description": kit.job_description,
        "generated_content": generated_content,
        "created_at": datetime.utcnow()
    }
    res = await db.application_kits.insert_one(data)
    data["id"] = str(res.inserted_id)
    return data


@router.post("/chain", response_model=ApplicationKitOut, status_code=status.HTTP_201_CREATED)
async def create_kit_chain(kit: ApplicationKitCreate, current_user=Depends(get_current_user)):
    """
    Generate application kit using chain approach with all entities:
    email, cover_letter, q_and_a, dsa, experiences, playlists
    """
    # Fetch resume
    resume = await db.resumes.find_one({"_id": ObjectId(kit.resume_id), "user_id": current_user.id})
    if not resume:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    
    # Generate content using chain approach
    generated_content = generate_application_kit_content_chain(resume.get("resume_data"), kit.job_description)
    
    # Store in DB
    data = {
        "user_id": current_user.id,
        "resume_id": kit.resume_id,
        "job_description": kit.job_description,
        "generated_content": generated_content,
        "generation_method": "chain",
        "created_at": datetime.utcnow()
    }
    res = await db.application_kits.insert_one(data)
    data["id"] = str(res.inserted_id)
    return data


@router.get("/", response_model=List[ApplicationKitOut])
async def list_kits(current_user=Depends(get_current_user)):
    cursor = db.application_kits.find({"user_id": current_user.id})
    kits = []
    async for doc in cursor:
        doc["id"] = str(doc["_id"])
        kits.append(doc)
    return kits


@router.get("/{kit_id}", response_model=ApplicationKitOut)
async def get_kit(kit_id: str, current_user=Depends(get_current_user)):
    oid = _obj_id(kit_id)
    doc = await db.application_kits.find_one({"_id": oid, "user_id": current_user.id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kit not found")
    doc["id"] = str(doc["_id"])
    return doc
