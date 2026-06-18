from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=schemas.PaymentsResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_payment(request: Request, payment: schemas.PaymentsCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    booking = crud.BookingsCRUD(db).get(payment.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to make payment for this booking")

    payments_crud = crud.PaymentsCRUD(db)
    return payments_crud.create(**payment.model_dump())


@router.get("/{payment_id}", response_model=schemas.PaymentsResponse)
@limiter.limit("30/minute")
def get_payment(request: Request, payment_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    payments_crud = crud.PaymentsCRUD(db)

    payment = payments_crud.get(payment_id=payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Get the booking to verify ownership
    booking = crud.BookingsCRUD(db).get(payment.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated booking not found"
        )

    if current_user.role != "admin" and booking.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this payment"
        )
    
    return payment


@router.get("/user/{user_id}", response_model=List[schemas.PaymentsResponse])
@limiter.limit("30/minute")
def get_user_payments(
    request: Request,
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return crud.PaymentsCRUD(db).get_payments_by_user(user_id=user_id)


@router.get("/owner/{owner_id}", response_model=List[schemas.PaymentsResponse])
def get_owner_payments(
    owner_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    payments_crud = crud.PaymentsCRUD(db)
    return payments_crud.get_payments_by_owner(owner_id=owner_id)