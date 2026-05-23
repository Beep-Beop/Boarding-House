# bookings.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from database import get_db
from models import Booking, Rooms

router = APIRouter(prefix="/bookings", tags=["bookings"])

class BookingCreate(BaseModel):
    booking_id: int
    user_id: int
    room_id: int
    check_in: date
    check_out: date
    status: Optional[str] = "pending"
    total_price: float
    notes: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

class BookingUpdate(BaseModel):
    booking_id: Optional[int] = None
    user_id: Optional[int] = None
    room_id: Optional[int] = None
    check_in: Optional[date] = None
    check_out: Optional[date] = None
    status: Optional[str] = None
    total_price: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None

@router.post("/")
def create_booking(data: BookingCreate, db: Session = Depends(get_db)):
    room = db.query(Rooms).filter(Rooms.room_id == data.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    new_booking = Booking(**data.dict())
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return {
        "message": "Booking created successfully",
        "booking": new_booking
    }

@router.get("/")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(Booking).all()
    return bookings

@router.patch("/{booking_id}")
def update_booking(booking_id: int, data: BookingUpdate, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail= "Booking not found")
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(booking, key, value)
    db.commit()
    db.refresh(booking)
    return {
        "message": "Booking updated successfully",
        "data": booking
    }


        

