from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/booking-history", tags=["Booking History"])


@router.get("/booking/{booking_id}", response_model=List[schemas.BookingHistoryResponse])
@limiter.limit("30/minute")
def get_booking_history(request: Request, booking_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    booking = crud.BookingsCRUD(db).get(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    # Get the listing to check if the user is the owner
    from src.models import Rooms, BoardingHouse
    room = db.query(Rooms).filter(Rooms.room_id == booking.room_id).first()
    listing = db.query(BoardingHouse).filter(BoardingHouse.listing_id == room.listing_id).first() if room else None

    if current_user.role != "admin" and current_user.user_id != booking.user_id and (not listing or listing.owner_id != current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this booking history"
        )

    return crud.BookingHistoryCRUD(db).get_history_by_booking(booking_id=booking_id)
