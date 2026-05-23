# rooms.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from database import get_db
from models import Room, BoardingHouse

router = APIRouter(prefix="/rooms", tags=["rooms"])

class RoomCreate(BaseModel):
    room_id: int
    listing_id: Optional[int] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price_per_month: Optional[float] = None
    availability: Optional[bool] = None
    Floor_level: Optional[int] = None
    
class RoomUpdate(BaseModel):
    listing_id: Optional[int] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price_per_month: Optional[float] = None
    availability: Optional[bool] = None
    Floor_level: Optional[int] = None

@router.post("/", response_model=RoomCreate)
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    boarding_house = db.query(BoardingHouse).filter(BoardingHouse.listing_id == room.listing_id).first()
    if not boarding_house:
        raise HTTPException(status_code=404, detail="Boarding house not found")

    new_room = Room(
        room_id=room.room_id,
        listing_id=room.listing_id,
        room_type=room.room_type,
        capacity=room.capacity,
        price_per_month=room.price_per_month,
        availability=room.availability,
        Floor_level=room.Floor_level
    )

    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    return {
        "message": "Room created successfully",
        "room": new_room
    }

@router.patch("/{room_id}")
def update_room(room_id: int, room_update: RoomUpdate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # If listing_id is being updated, ensure the boarding house exists
    if room_update.listing_id is not None:
        boarding_house = db.query(BoardingHouse).filter(BoardingHouse.listing_id == room_update.listing_id).first()
        if not boarding_house:
            raise HTTPException(status_code=404, detail="Boarding house not found")

    update_data = room_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(room, key, value)

    db.commit()
    db.refresh(room)

    return {
        "message": "Room updated successfully",
        "data": room
    }