from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from src import crud, schemas, database, security
from typing import List

router = APIRouter(prefix="/photos", tags=["Photos"])

# In-memory storage (just a list of dictionaries, no class models)
photo_storage = []

@router.post("/")
async def upload_photo(
    file: UploadFile = File(...),
    description: str = "",
    db: Session = Depends()
):
    """Upload a new photo"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Directly create dictionary data, no model class
    photo_data = {
        "id": len(photo_storage) + 1,
        "filename": file.filename,
        "description": description
    }
    photo_storage.append(photo_data)
    return {"message": "Photo uploaded successfully", "data": photo_data}

@router.get("/")
async def get_all_photos(db: Session = Depends()):
    """Get all uploaded photos"""
    return {"total": len(photo_storage), "photos": photo_storage}