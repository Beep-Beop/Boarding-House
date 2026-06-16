from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

# 1. Always declare the router at the top
router = APIRouter(prefix="/bookings", tags=["Bookings"])

# 2. One function per endpoint

# POST / → Create a resource
@router.post("/", response_model=schemas.BookingsResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_booking(request: Request, booking: schemas.BookingsCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    booking_crud = crud.BookingsCRUD(db)

    if current_user.role != "admin" and current_user.user_id != booking.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create bookings for yourself"
        )

    return booking_crud.create(**booking.model_dump())


# PATCH /{id}/status → Partial update on a specific field
# Enforces the rule: No loose query parameters. Everything is encapsulated in the schema payload.
@router.patch("/{booking_id}/status", response_model=schemas.BookingsResponse)
@limiter.limit("5/minute")
def update_booking_status(
    request: Request,
    booking_id: int, 
    status_update: schemas.BookingStatusUpdate,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    booking_crud = crud.BookingsCRUD(db)
    booking = booking_crud.get(booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    room = crud.RoomsCRUD(db).get(booking.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    bh = crud.BoardingHousesCRUD(db).get(room.listing_id)

    is_student_cancel = (
        current_user.role == "student"
        and current_user.user_id == booking.user_id
        and status_update.status == "cancelled"
        and booking.status == "pending"
    )

    is_owner_or_admin = (
        current_user.role == "admin"
        or (bh and bh.owner_id == current_user.user_id)
    )

    if not is_student_cancel and not is_owner_or_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this booking"
        )

    booking = booking_crud.update_status(
        booking_id=booking_id,
        new_status=status_update.status,
        changed_by_user_id=current_user.user_id
    )

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    return booking


# GET /owner/{owner_id} → Fetch bookings for all rooms owned by the given owner
@router.get("/owner/{owner_id}", response_model=List[schemas.BookingsResponse])
def get_owner_bookings(owner_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    booking_crud = crud.BookingsCRUD(db)
    return booking_crud.get_owner_bookings(owner_id=owner_id)


# GET /user/{user_id} → Fetch a collection of records filtered by user
@router.get("/user/{user_id}", response_model=List[schemas.BookingsResponse])
def get_user_bookings(user_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own bookings"
        )

    booking_crud = crud.BookingsCRUD(db)

    bookings = booking_crud.get_user_bookings(user_id=user_id)

    return bookings