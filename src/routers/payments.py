from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter
from src.models import BoardingHouse, Rooms, Bookings, Users

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/booking/{booking_id}", response_model=List[schemas.PaymentsResponse])
@limiter.limit("30/minute")
def get_booking_payments(
    request: Request,
    booking_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    booking = crud.BookingsCRUD(db).get(booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    room = crud.RoomsCRUD(db).get(booking.room_id)
    bh = crud.BoardingHousesCRUD(db).get(room.listing_id) if room else None

    is_owner = bh and bh.owner_id == current_user.user_id
    if current_user.role != "admin" and booking.user_id != current_user.user_id and not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    payments_crud = crud.PaymentsCRUD(db)
    return payments_crud.get_payments_by_booking(booking_id)


@router.post("/", response_model=schemas.PaymentsResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_payment(
    request: Request,
    payment_data: schemas.PaymentsCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    booking_crud = crud.BookingsCRUD(db)
    booking = booking_crud.get(payment_data.booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    room = crud.RoomsCRUD(db).get(booking.room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    listing = crud.BoardingHousesCRUD(db).get(room.listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    if current_user.role != "admin" and listing.owner_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the property owner can create payments")

    payments_crud = crud.PaymentsCRUD(db)
    return payments_crud.create(
        booking_id=payment_data.booking_id,
        amount=payment_data.amount,
        method=payment_data.method,
        reference_no=payment_data.reference_no,
        period_start=payment_data.period_start,
        period_end=payment_data.period_end,
        due_date=payment_data.due_date,
        notes=payment_data.notes,
        tenant_id=booking.user_id,
    )


@router.get("/owner/pending", response_model=List[schemas.PaymentApprovalResponse])
@limiter.limit("30/minute")
def get_owner_pending_payments(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    owner_id = current_user.user_id
    payments_crud = crud.PaymentsCRUD(db)
    payments = payments_crud.get_pending_by_owner(owner_id=owner_id)

    result = []
    for pay in payments:
        booking = db.query(Bookings).filter(Bookings.booking_id == pay.booking_id).first()
        tenant = db.query(Users).filter(Users.user_id == booking.user_id).first() if booking else None
        room = db.query(Rooms).filter(Rooms.room_id == booking.room_id).first() if booking else None
        bh = db.query(BoardingHouse).filter(BoardingHouse.listing_id == room.listing_id).first() if room else None
        result.append(schemas.PaymentApprovalResponse(
            payment_id=pay.payment_id,
            booking_id=pay.booking_id,
            tenant_id=pay.tenant_id,
            amount=pay.amount,
            method=pay.method,
            status=pay.status,
            period_start=pay.period_start,
            period_end=pay.period_end,
            due_date=pay.due_date,
            submitted_at=pay.submitted_at,
            paid_at=pay.paid_at,
            verified_by=pay.verified_by,
            reference_no=pay.reference_no,
            notes=pay.notes,
            tenant_name=tenant.name if tenant else None,
            property_name=bh.bh_name if bh else None,
        ))
    return result


@router.patch("/{payment_id}/submit", response_model=schemas.PaymentsResponse)
@limiter.limit("5/minute")
def submit_payment(
    request: Request,
    payment_id: int,
    submit_data: schemas.PaymentSubmit,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    payments_crud = crud.PaymentsCRUD(db)
    payment = payments_crud.get(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    booking = crud.BookingsCRUD(db).get(payment.booking_id)
    if not booking or booking.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your payment")

    if payment.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Payment already {payment.status}")

    return payments_crud.submit_payment(
        payment_id=payment_id,
        method=submit_data.method,
        reference_no=submit_data.reference_no,
        notes=submit_data.notes,
        tenant_id=current_user.user_id
    )


@router.patch("/{payment_id}/verify", response_model=schemas.PaymentsResponse)
@limiter.limit("10/minute")
def verify_payment(
    request: Request,
    payment_id: int,
    verify_data: schemas.PaymentVerify,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    payments_crud = crud.PaymentsCRUD(db)
    payment = payments_crud.get(payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    booking = crud.BookingsCRUD(db).get(payment.booking_id)
    room = crud.RoomsCRUD(db).get(booking.room_id) if booking else None
    bh = crud.BoardingHousesCRUD(db).get(room.listing_id) if room else None

    is_owner = bh and bh.owner_id == current_user.user_id
    if current_user.role != "admin" and not is_owner:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can verify payments")

    if payment.status != "paid":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot verify payment with status '{payment.status}'")

    return payments_crud.verify_payment(
        payment_id=payment_id,
        new_status=verify_data.status,
        verified_by=current_user.user_id
    )


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
