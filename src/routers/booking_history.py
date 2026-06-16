from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/booking-history", tags=["Booking History"])


@router.get("/booking/{booking_id}", response_model=List[schemas.BookingHistoryResponse])
def get_booking_history(booking_id: int, db: Session = Depends(database.get_db)):
    if not crud.BookingsCRUD(db).get(booking_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return crud.BookingHistoryCRUD(db).get_history_by_booking(booking_id=booking_id)
