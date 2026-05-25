from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

# 1. Always declare the router at the top
# prefix = the URL base (/bookings)
# tags   = groups it in the Swagger docs
router = APIRouter(prefix="/bookings", tags=["Bookings"])


# POST / → Create a resource
# - status_code=201 for creation, not the default 200
# - response_model tells FastAPI what shape to return
@router.post("/", response_model=schemas.BookingsResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking: schemas.BookingsCreate, db: Session = Depends(database.get_db)):
    # 3. Always instantiate your CRUD class first, passing the db session
    booking_crud = crud.BookingsCRUD(db)

    # 4. Guard clauses BEFORE the main operation (None needed for basic creation)

    # 5. One CRUD call. Return directly — FastAPI + Pydantic handles serialization
    return booking_crud.create(**booking.model_dump())


# PATCH /{id}/status → Partial update on a specific field
# Note the sub-path /status — it's explicit about what's being changed
@router.patch("/{booking_id}/status", response_model=schemas.BookingsResponse)
def update_booking_status(
    booking_id: int, 
    status_update: schemas.BookingUpdate, 
    changed_by_user_id: int,  # Required context for database tracking table constraints
    db: Session = Depends(database.get_db)
):
    # 3. Always instantiate your CRUD class first, passing the db session
    booking_crud = crud.BookingsCRUD(db)

    # 5. Call exactly ONE CRUD method to do the work
    # Our CRUD update methods return the object or None — not a bool
    # So we can check and return in one shot, no second DB call needed
    booking = booking_crud.update_status(
        booking_id=booking_id, 
        new_status=status_update.status, 
        changed_by_user_id=changed_by_user_id
    )

    # 6. Standard 404 pattern — check result and raise HTTP errors if something went wrong
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

    # 7. Return the result directly — FastAPI + Pydantic handles list serialization
    return bookings