from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import os

from src.database import get_db, Base, engine
from src.crud import UserCRUD, PhotoCRUD
from src.storage import StorageService
from src.models import Photo, EntityTypeEnum

app = FastAPI(title="Aiven + R2 Photo API")
storage_service = StorageService()

@app.get("/user/{email}")
def read_user(email: str, db: Session = Depends(get_db)):
    user_logic = UserCRUD(db)
    user = user_logic.get_user_by_email(email)

    if not user:
        return{"error": "User not found"}
    return user

@app.post("/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    entity_type: EntityTypeEnum = Form(...),
    entity_id: int = Form(...),
    is_primary: bool = Form(False),
    sort_order: int = Form(0),
    db: Session = Depends(get_db)
):
    content = await file.read()
    
    file_extension = os.path.splitext(file.filename)[1]
    r2_key = f"photos/{entity_type.value}/{entity_id}/{uuid.uuid4()}{file_extension}"
    
    upload_success = storage_service.upload_file(content, r2_key)
    if not upload_success:
        raise HTTPException(status_code=500, detail="Failed to upload photo to Cloudflare R2.")

    crud = PhotoCRUD(db)
    try:
        photo = crud.create(
            entity_type=entity_type,
            entity_id=entity_id,
            photo_url=r2_key,
            is_primary=is_primary,
            sort_order=sort_order
        )
        return {
            "message": "Photo uploaded successfully!",
            "photo_id": photo.photo_id,
            "photo_url": photo.photo_url
        }
    except Exception as e:
        storage_service.delete_file(r2_key)
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/photos")
def list_photos(db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    return [
        {
            "photo_id": p.photo_id, 
            "entity_type": p.entity_type,
            "entity_id": p.entity_id,
            "photo_url": p.photo_url,
            "is_primary": p.is_primary
        } 
        for p in photos
    ]