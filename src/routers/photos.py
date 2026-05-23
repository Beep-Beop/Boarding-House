from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List

router = APIRouter(prefix="/photos", tags=["Photos"])

# In-memory storage (replace with database in production)
photo_storage = []

@router.post("/")
async def upload_photo(file: UploadFile = File(...), description: str = ""):
    """Upload a new photo"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    photo_data = {
        "id": len(photo_storage) + 1,
        "filename": file.filename,
        "description": description
    }
    photo_storage.append(photo_data)
    return {"message": "Photo uploaded successfully", "data": photo_data}

@router.get("/")
async def get_all_photos():
    """Get all uploaded photos"""
    return {"total": len(photo_storage), "photos": photo_storage}