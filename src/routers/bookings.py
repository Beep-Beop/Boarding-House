from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

# 1. Always declare the router at the top
router = APIRouter(prefix="/bookings", tags=["Bookings"])

# 2. One function per endpoint

# POST / → Create a resource
@router.post("/", response_model=schemas.BookingsResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking: schemas.BookingsCreate, db: Session = Depends(database.get_db)):
    # 3. Always instantiate your CRUD class first, passing the db session
    booking_crud = crud.BookingsCRUD(db)

    # 4. Guard clauses BEFORE the main operation (None required for creation)

    # 5. One CRUD call. Return directly.
    return booking_crud.create(**booking.model_dump())


# PATCH /{id}/status → Partial update on a specific field
# Enforces the rule: No loose query parameters. Everything is encapsulated in the schema payload.
@router.patch("/{booking_id}/status", response_model=schemas.BookingsResponse)
def update_booking_status(
    booking_id: int, 
    status_update: schemas.BookingStatusUpdate,  # Clean: All inputs live inside this schema block
    db: Session = Depends(database.get_db)
):
    # 3. Always instantiate your CRUD class first, passing the db session
    booking_crud = crud.BookingsCRUD(db)

    # 5. Call exactly ONE CRUD method to do the work
    # We unpack the entire validated schema payload directly into the database repository
    booking = booking_crud.update_status(
        booking_id=booking_id, 
        **status_update.model_dump()
    )

    # 6. Standard 404 pattern
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # 7. Return the result directly
    return booking


# GET /user/{user_id} → Fetch a collection of records filtered by user
@router.get("/user/{user_id}", response_model=List[schemas.BookingsResponse])
def get_user_bookings(user_id: int, db: Session = Depends(database.get_db)):
    # 3. Always instantiate your CRUD class first, passing the db session
    booking_crud = crud.BookingsCRUD(db)

    # 5. Call exactly ONE CRUD method to do the work
    bookings = booking_crud.get_user_bookings(user_id=user_id)

    # 7. Return the result directly — FastAPI handles array serialization
    return bookings