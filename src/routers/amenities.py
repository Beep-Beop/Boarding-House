from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/amenities", tags=["Amenities"])


@router.post("/", response_model=schemas.AmenitiesResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_amenity(request: Request, amenity: schemas.AmenitiesCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return crud.AmenitiesCRUD(db).create(**amenity.model_dump())


@router.get("/", response_model=List[schemas.AmenitiesResponse])
def get_all_amenities(db: Session = Depends(database.get_db)):
    return crud.AmenitiesCRUD(db).get_all()


@router.get("/{amenity_id}", response_model=schemas.AmenitiesResponse)
def get_amenity(amenity_id: int, db: Session = Depends(database.get_db)):
    amenity = crud.AmenitiesCRUD(db).get(amenity_id)
    if not amenity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found")
    return amenity


@router.delete("/{amenity_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def delete_amenity(request: Request, amenity_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    amenity = crud.AmenitiesCRUD(db).get(amenity_id)
    if not amenity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Amenity not found")
    crud.AmenitiesCRUD(db).delete(amenity_id)
