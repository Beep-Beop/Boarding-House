from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from src import crud, schemas, database
from src.storage import StorageService
from src.config import Settings

router = APIRouter(prefix="/photos", tags=["Photos"])

storage_service = StorageService()

@router.post("/", response_model=schemas.PhotoResponse)
async def upload_photo(
    entity_type: str = Form(..., description="Must be 'listing' or 'room'"),
    entity_id: int = Form(...),
    is_primary: bool = Form(False),
    sort_order: int = Form(0),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    
    if entity_type not in ['listing', 'room']:
        raise HTTPException(status_code=422, detail="entity_type must be 'listing or 'room'")
    
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    file_content = await file.read()

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    success = storage_service.upload_file(file_content, unique_filename)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to upload image to Cloudflare R2")
    
    public_url = f"will put url here later"

    photo_crud = crud.PhotoCRUD(db)
    db_photo = photo_crud.create(
        entity_type=entity_type,
        entity_id=entity_id,
        photo_url=public_url,
        is_primary=is_primary,
        sort_order=sort_order
    )

    return db_photo

@router.get("/{entity_type}/{entity_id}", response_model=List[schemas.PhotoResponse])
def get_photo(entity_type: str, entity_id: int, db: Session = Depends(database.get_db())):
    if entity_type not in ['listing', 'room']:
        raise HTTPException(status_code=422, detail="entity_type must be 'listing', or 'room'")
    
    photo_crud = crud.PhotoCRUD(db)

    return photo_crud.get_photos_for_entity(entity_type=entity_type, entity_id=entity_id)
