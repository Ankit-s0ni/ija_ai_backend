from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List
from datetime import datetime
from bson import ObjectId

from app.schemas.resume import ResumeCreate, ResumeOut, ResumeUpdate, ResumeCreateFromPDF
from app.core.database import db
from app.core.security import get_current_user
from app.services.pdf_service import PDFParsingService

router = APIRouter()


def _obj_id(id: str):
    try:
        return ObjectId(id)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid resume ID")


@router.post("/", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def create_resume(resume: ResumeCreate, current_user=Depends(get_current_user)):
    data = resume.model_dump()
    data.update({
        "user_id": current_user.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    result = await db.resumes.insert_one(data)
    data["id"] = str(result.inserted_id)
    return data


@router.get("/", response_model=List[ResumeOut])
async def list_resumes(current_user=Depends(get_current_user)):
    cursor = db.resumes.find({"user_id": current_user.id})
    resumes = []
    async for doc in cursor:
        # Transform the document to match ResumeOut schema
        resume_data = {
            "id": str(doc["_id"]),
            "resume_name": doc.get("resume_name", ""),
            "resume_data": {
                "content": doc.get("content", ""),
                "personal_info": doc.get("personal_info", {}),
                "education": doc.get("education", []),
                "skills": doc.get("skills", []),
                "experience": doc.get("experience", []),
                "projects": doc.get("projects", [])
            },
            "user_id": doc.get("user_id", ""),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at")
        }
        resumes.append(resume_data)
    return resumes


@router.get("/{resume_id}", response_model=ResumeOut)
async def get_resume(resume_id: str, current_user=Depends(get_current_user)):
    oid = _obj_id(resume_id)
    doc = await db.resumes.find_one({"_id": oid, "user_id": current_user.id})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    
    # Transform the document to match ResumeOut schema
    resume_data = {
        "id": str(doc["_id"]),
        "resume_name": doc.get("resume_name", ""),
        "resume_data": {
            "content": doc.get("content", ""),
            "personal_info": doc.get("personal_info", {}),
            "education": doc.get("education", []),
            "skills": doc.get("skills", []),
            "experience": doc.get("experience", []),
            "projects": doc.get("projects", [])
        },
        "user_id": doc.get("user_id", ""),
        "created_at": doc.get("created_at"),
        "updated_at": doc.get("updated_at")
    }
    return resume_data


@router.put("/{resume_id}", response_model=ResumeOut)
async def update_resume(resume_id: str, resume: ResumeUpdate, current_user=Depends(get_current_user)):
    oid = _obj_id(resume_id)
    data = {k: v for k, v in resume.dict().items() if v is not None}
    if not data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields provided for update")
    data["updated_at"] = datetime.utcnow()
    result = await db.resumes.update_one({"_id": oid, "user_id": current_user.id}, {"$set": data})
    if result.modified_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found or no changes made")
    doc = await db.resumes.find_one({"_id": oid})
    doc["id"] = str(doc["_id"])
    return doc


@router.post("/upload-pdf", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
async def upload_resume_pdf(
    resume_name: str = Form(...),
    file: UploadFile = File(...),
    current_user=Depends(get_current_user)
):
    """Upload and parse a PDF resume file"""
    
    # Validate file type
    if not file.content_type == "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    # Validate file size (10MB max)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size too large. Maximum 10MB allowed."
        )
    
    try:
        # Read file content
        pdf_content = await file.read()
        
        # Extract text from PDF
        text_content = await PDFParsingService.extract_text_from_pdf(pdf_content)
        
        if not text_content.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from PDF. Please ensure the PDF contains readable text."
            )
        
        # Parse structured data
        structured_data = PDFParsingService.parse_structured_data(text_content, resume_name)
        
        # Prepare data for database
        resume_data = {
            "resume_name": resume_name,
            "content": text_content,
            "personal_info": structured_data.personal_info.model_dump(),
            "education": [edu.model_dump() for edu in structured_data.education],
            "skills": structured_data.skills,
            "experience": [exp.model_dump() for exp in structured_data.experience],
            "projects": [proj.model_dump() for proj in structured_data.projects],
            "user_id": current_user.id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to database
        result = await db.resumes.insert_one(resume_data)
        resume_data["id"] = str(result.inserted_id)
        
        # Convert to ResumeOut format
        response_data = {
            "id": resume_data["id"],
            "resume_name": resume_data["resume_name"],
            "resume_data": {
                "content": resume_data["content"],
                "personal_info": resume_data["personal_info"],
                "education": resume_data["education"],
                "skills": resume_data["skills"],
                "experience": resume_data["experience"],
                "projects": resume_data["projects"]
            },
            "user_id": resume_data["user_id"],
            "created_at": resume_data["created_at"],
            "updated_at": resume_data["updated_at"]
        }
        
        return response_data
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the PDF: {str(e)}"
        )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(resume_id: str, current_user=Depends(get_current_user)):
    oid = _obj_id(resume_id)
    result = await db.resumes.delete_one({"_id": oid, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return None
