# bookings.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=schemas.BookingResponse)
def create_booking(
    booking: schemas.BookingCreate,
    db: Session = Depends(database.get_db)
):
    booking_crud = crud.BookingCRUD(db)

    return booking_crud.create(**booking.model_dump())


@router.patch("/{booking_id}", response_model=schemas.BookingResponse)
def update_booking(
    booking_id: int,
    booking: schemas.BookingUpdate,
    db: Session = Depends(database.get_db)
):
    booking_crud = crud.BookingCRUD(db)

    existing_booking = booking_crud.get(booking_id)

    if not existing_booking:
        raise HTTPException(status_code=404, detail="Booking Not Found")

    return booking_crud.update(
        booking_id,
        **booking.model_dump(exclude_unset=True)
    )


@router.get("/{booking_id}", response_model=schemas.BookingResponse)
def read_booking(
    booking_id: int,
    db: Session = Depends(database.get_db)
):
    booking = crud.BookingCRUD(db).get(booking_id)

    if not booking:
        raise HTTPException(status_code=404, detail="Booking Not Found")

    return booking