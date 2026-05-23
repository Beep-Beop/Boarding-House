# boarding_house.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List 

from ..database import get_db
from ..models import BoardingHouse

router = APIRouter(prefix="/boarding-houses",tags=["boarding-houses"])

class BoardingHouseCreate(BaseModel):
    listing_id: int
    owner_id: int
    location_id: str
    bh_name: str 
    description: Optional[str] = None
    price_range: Optional[str] = None
    status: Optional[str] = "pending"
    bh_created_at: Optional[str] = None
    is_verified: Optional[bool] = None
    permit_url: Optional[str] = None
    min_stay_months: Optional[int] = 1
    rules: Optional[str] = None

class BoardingHouseUpdate(BaseModel):
    bh_name: Optional[str] = None
    description: Optional[str] = None
    price_range: Optional[str] = None
    status: Optional[str] = None
    is_verified: Optional[bool] = None
    permit_url: Optional[str] = None
    min_stay_months: Optional[int] = None
    rules: Optional[str] = None

class BoardingHouseResponse(BaseModel):
    listing_id: int
    owner_id: int
    Location_id: str
    bh_name: str
    description: Optional[str] = None
    price_range: Optional[str] = None
    status: Optional[str] = None
    bh_created_at: Optional[str] = None
    is_verified: Optional[bool] = None
    permit_url: Optional[str]
    min_stay_months: Optional[int]
    rules: Optional[str]
    class Config:
        orm_mode = True


@router.post("/", response_model=BoardingHouseResponse)
def create_boarding_house(bh: BoardingHouseCreate, db: Session = Depends(get_db)):
    new_boarding_house = BoardingHouse(**bh.dict())
    db.add(new_boarding_house)
    db.commit()
    db.refresh(new_boarding_house)

    return new_boarding_house


@router.get("/", response_model=List[BoardingHouseResponse])
def get_boarding_houses(
    db: Session = Depends(get_db)
):
    boarding_houses = db.query(BoardingHouse).all()
    return boarding_houses

@router.patch("/{listing_id}", response_model=BoardingHouseResponse)
def update_boarding_house(
    listing_id: int,
    bh_update: BoardingHouseUpdate,
    db: Session = Depends(get_db)
):
    
    boarding_house = db.query(BoardingHouse).filter(BoardingHouse.listing_id == listing_id).first()
    if not boarding_house:
        raise HTTPException(status_code=404, detail="Boarding house not found")
    
    update_data = bh_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(boarding_house, key, value)
        db.commit()
        db.refresh(boarding_house)

        return boarding_house






