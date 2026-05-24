from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingsCreate, db: Session = Depends(database.get_db)):
    booking_crud = crud.BookingCRUD(db)

    return booking_crud.create(**booking.model_dump())


@router.patch("/{booking_id}/status", response_model=schemas.BookingResponse)
def update_booking(booking_id: int, status_update: schemas.BookingUpdate, db: Session = Depends(database.get_db)):
    booking_crud = crud.BookingCRUD(db)

    updated_booking = booking_crud.update(booking_id, **status_update.model_dump(exclude_unset=True))

    if not updated_booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    return updated_booking

@router.get("/user/{user_id}", response_model=schemas.BookingResponse)
def read_booking(user_id: int, db: Session = Depends(database.get_db)
):
    booking_crud = crud.BookingCRUD(db)

    history = booking_crud.get_by_user_id(user_id)

    return history