from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from typing import List
import uuid
from pydantic import BaseModel
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter
from src.storage import StorageService

router = APIRouter(prefix="/photos", tags=["Photos"])

storage_service = StorageService()


def _get_entity_owner(db: Session, entity_type: str, entity_id: int) -> int | None:
    if entity_type == "listing":
        listing = crud.BoardingHousesCRUD(db).get(entity_id)
        return listing.owner_id if listing else None
    elif entity_type == "room":
        room = crud.RoomsCRUD(db).get(entity_id)
        if room:
            listing = crud.BoardingHousesCRUD(db).get(room.listing_id)
            return listing.owner_id if listing else None
    return None


class FileUploadResponse(BaseModel):
    url: str
    filename: str


@router.post("/upload", response_model=FileUploadResponse)
@limiter.limit("10/minute")
async def upload_file(request: Request, file: UploadFile = File(...), current_user: schemas.TokenData = Depends(get_current_user)):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided")

    MAX_FILE_SIZE = 10 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="File too large. Maximum size is 10MB.")

    magic = contents[:12]
    ALLOWED_MAGIC = [
        (b"\xff\xd8\xff", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
    ]
    is_webp = magic[:4] == b"RIFF" and magic[8:12] == b"WEBP"
    is_valid = any(magic.startswith(sig) for sig, _ in ALLOWED_MAGIC) or is_webp
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed.")

    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    folder = "uploads"

    success = storage_service.upload_file(contents, f"{folder}/{unique_filename}")
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload file")

    public_url = storage_service.get_public_url(unique_filename, folder=folder)
    return FileUploadResponse(url=public_url, filename=unique_filename)

@router.post("/", response_model=schemas.PhotoResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_photo(request: Request, file: UploadFile = File(...), metadata: schemas.PhotoUploadMetadata = Depends(), db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    photo_crud = crud.PhotosCRUD(db)

    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="No file provided"
        )
    
    if metadata.entity_type == "listing":
        if not crud.BoardingHousesCRUD(db).get(metadata.entity_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Boarding house not found"
            )
    elif metadata.entity_type == "room":
        if not crud.RoomsCRUD(db).get(metadata.entity_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Room not found"
            )

    MAX_FILE_SIZE = 5 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="File too large. Maximum size is 5MB."
        )

    magic = contents[:12]
    ALLOWED_MAGIC = [
        (b"\xff\xd8\xff", "image/jpeg"),
        (b"\x89PNG\r\n\x1a\n", "image/png"),
    ]
    is_webp = magic[:4] == b"RIFF" and magic[8:12] == b"WEBP"
    is_valid = any(magic.startswith(sig) for sig, _ in ALLOWED_MAGIC) or is_webp
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed."
        )

    file_content = contents
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    folder = metadata.entity_type  # "listing" or "room"
    success = storage_service.upload_file(file_content, f"{folder}/{unique_filename}")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to upload image to Cloudflare R2"
        )
    
    public_url = storage_service.get_public_url(unique_filename, folder=folder)

    return photo_crud.create(photo_url=public_url, **metadata.model_dump())


@router.post("/from_url", response_model=schemas.PhotoResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_photo_from_url(request: Request, photo: schemas.PhotoCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    photo_crud = crud.PhotosCRUD(db)
    return photo_crud.create(**photo.model_dump())


@router.delete("/upload/{filename}")
@limiter.limit("30/minute")
async def delete_upload(request: Request, filename: str, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    folder = "uploads"
    if ".." in filename or "/" in filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
    photo_crud = crud.PhotosCRUD(db)
    matching_photos = photo_crud.get_photos_by_url(f"{folder}/{filename}")
    if matching_photos:
        for photo in matching_photos:
            if current_user.role != "admin":
                entity_owner = _get_entity_owner(db, photo.entity_type, photo.entity_id)
                if entity_owner != current_user.user_id:
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this file")
    elif current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this file")
    success = storage_service.delete_file(f"{folder}/{filename}")
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return {"detail": "File deleted"}

@router.get("/{entity_type}/{entity_id}", response_model=List[schemas.PhotoResponse])
def get_photos(entity_type: str, entity_id: int, db: Session = Depends(database.get_db)):
    photo_crud = crud.PhotosCRUD(db)

    if entity_type not in ['listing', 'room']:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
            detail="entity_type must be 'listing' or 'room'"
        )
    
    return photo_crud.get_photos_for_entity(entity_type=entity_type, entity_id=entity_id)