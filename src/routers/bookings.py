from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from src import crud, models, schemas, database
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

    is_student_move_in_request = (
        current_user.role == "student"
        and current_user.user_id == booking.user_id
        and status_update.status == "active"
        and booking.status == "approved"
    )

    is_owner_or_admin = (
        current_user.role == "admin"
        or (bh and bh.owner_id == current_user.user_id)
    )

    if not is_student_cancel and not is_student_move_in_request and not is_owner_or_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this booking"
        )

    # Handle student move-in request (flag instead of status change)
    if is_student_move_in_request:
        payments_crud = crud.PaymentsCRUD(db)
        payments = payments_crud.get_payments_by_booking(booking_id)
        if not any(p.status == "completed" for p in payments):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment is required before requesting move-in. Please submit a payment first."
            )

        booking.move_in_requested = True
        db.commit()
        db.refresh(booking)

        history_entry = models.BookingHistory(
            booking_id=booking_id, old_status=booking.status, new_status="move_in_requested",
            changed_by=current_user.user_id
        )
        db.add(history_entry)
        db.commit()
        db.refresh(booking)
        return booking

    # Owner transitions
    valid_owner_transitions = {
        "pending": ["approved", "cancelled"],
        "approved": ["active", "cancelled"],
        "active": ["cancelled"],
        "cancelled": ["pending"],
    }

    if is_owner_or_admin:
        allowed = valid_owner_transitions.get(booking.status, [])
        if status_update.status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot change booking from {booking.status} to {status_update.status}"
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

    if status_update.status == "approved" and booking.check_in and booking.check_out:
        payments_crud = crud.PaymentsCRUD(db)
        payments_crud.create_monthly_payments(
            booking_id=booking_id,
            amount=room.price_per_month,
            check_in=booking.check_in,
            check_out=booking.check_out
        )

    return booking


# GET /owner/{owner_id} → Fetch bookings for all rooms owned by the given owner
@router.get("/owner/{owner_id}", response_model=List[schemas.BookingsResponse])
def get_owner_bookings(owner_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    booking_crud = crud.BookingsCRUD(db)
    return booking_crud.get_owner_bookings(owner_id=owner_id)


# GET /owner/{owner_id}/enriched → Owner: get enriched bookings with optional status/search filter
@router.get("/owner/{owner_id}/enriched", response_model=List[schemas.BookingAdminResponse])
def get_owner_bookings_enriched(
    owner_id: int,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    booking_crud = crud.BookingsCRUD(db)
    enriched = booking_crud.get_owner_bookings_enriched(owner_id=owner_id, status=status, search=search)
    result = []
    for item in enriched:
        b = item["booking"]
        room = item["room"]
        listing = item["listing"]
        tenant = item["tenant"]
        result.append(schemas.BookingAdminResponse(
            booking_id=b.booking_id, user_id=b.user_id, room_id=b.room_id,
            check_in=b.check_in, check_out=b.check_out, status=b.status,
            total_price=b.total_price, notes=b.notes, created_at=b.created_at,
            updated_at=b.updated_at,
            tenant_name=tenant.name if tenant else None,
            tenant_email=tenant.email if tenant else None,
            tenant_phone=tenant.phone if tenant else None,
            account_setup_complete=tenant.account_setup_complete if tenant else None,
            move_in_requested=item.get("move_in_requested"),
            property_name=listing.bh_name if listing else None,
            property_type=listing.property_type if listing else None,
            listing_id=listing.listing_id if listing else None,
            room_number=room.room_id if room else None,
            room_type=room.room_type if room else None,
            payment_status=item["payment_status"],
            payment_method=item["payment_method"],
            payment_amount=item["payment_amount"],
        ))
    return result


# GET /owner/{owner_id}/stats → Owner: get booking stats
@router.get("/owner/{owner_id}/stats", response_model=schemas.BookingStats)
def get_owner_booking_stats(
    owner_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.user_id != owner_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    booking_crud = crud.BookingsCRUD(db)
    return booking_crud.get_owner_booking_stats(owner_id=owner_id)


# GET /{booking_id}/owner-detail → Owner: get full booking detail they own
@router.get("/{booking_id}/owner-detail", response_model=schemas.BookingDetailResponse)
@limiter.limit("30/minute")
def get_owner_booking_detail(
    request: Request,
    booking_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    booking_crud = crud.BookingsCRUD(db)
    data = booking_crud.get_booking_detail(booking_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    b = data["booking"]
    room = data["room"]
    listing = data["listing"]
    tenant = data["tenant"]
    owner = data["owner"]
    payments = data["payments"]
    history = data["history"]

    if current_user.role == "owner" and (not listing or listing.owner_id != current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this property")

    payment_status = payments[0].status if payments else None
    payment_method = payments[0].method if payments else None
    payment_amount = payments[0].amount if payments else None
    address = None
    if listing and listing.location_id:
        loc = crud.LocationsCRUD(db).get(listing.location_id)
        if loc:
            address = f"{loc.street or ''}, {loc.barangay or ''}, {loc.city or ''}, {loc.province or ''}".strip(", ")
    payment_responses = [schemas.PaymentsResponse.model_validate(p) for p in payments]
    history_responses = [schemas.BookingHistoryResponse.model_validate(h) for h in history]
    return schemas.BookingDetailResponse(
        booking_id=b.booking_id, user_id=b.user_id, room_id=b.room_id,
        check_in=b.check_in, check_out=b.check_out, status=b.status,
        total_price=b.total_price, notes=b.notes, created_at=b.created_at,
        updated_at=b.updated_at,
        tenant_name=tenant.name if tenant else None,
        tenant_email=tenant.email if tenant else None,
        tenant_phone=tenant.phone if tenant else None,
        account_setup_complete=tenant.account_setup_complete if tenant else None,
        move_in_requested=b.move_in_requested,
        property_name=listing.bh_name if listing else None,
        property_type=listing.property_type if listing else None,
        room_number=room.room_id if room else None,
        room_type=room.room_type if room else None,
        payment_status=payment_status,
        payment_method=payment_method,
        payment_amount=payment_amount,
        payments=payment_responses,
        history=history_responses,
        listing_id=listing.listing_id if listing else None,
        owner_name=owner.name if owner else None,
        property_address=address,
    )


# GET /all → Admin: get all bookings with enriched data
@router.get("/all", response_model=dict)
def get_all_bookings(
    request: Request,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    booking_crud = crud.BookingsCRUD(db)
    bookings, total = booking_crud.get_all_bookings(status=status, search=search, page=page, limit=limit)
    result = []
    for b in bookings:
        room = crud.RoomsCRUD(db).get(b.room_id)
        listing = crud.BoardingHousesCRUD(db).get(room.listing_id) if room else None
        tenant = crud.UsersCRUD(db).get(b.user_id)
        payments = crud.PaymentsCRUD(db).get_payments_by_booking(b.booking_id)
        payment_status = payments[0].status if payments else None
        payment_method = payments[0].method if payments else None
        payment_amount = payments[0].amount if payments else None
        result.append(schemas.BookingAdminResponse(
            booking_id=b.booking_id, user_id=b.user_id, room_id=b.room_id,
            check_in=b.check_in, check_out=b.check_out, status=b.status,
            total_price=b.total_price, notes=b.notes, created_at=b.created_at,
            updated_at=b.updated_at,
            tenant_name=tenant.name if tenant else None,
            tenant_email=tenant.email if tenant else None,
            tenant_phone=tenant.phone if tenant else None,
            account_setup_complete=tenant.account_setup_complete if tenant else None,
            move_in_requested=b.move_in_requested,
            property_name=listing.bh_name if listing else None,
            property_type=listing.property_type if listing else None,
            listing_id=listing.listing_id if listing else None,
            room_number=room.room_id if room else None,
            room_type=room.room_type if room else None,
            payment_status=payment_status,
            payment_method=payment_method,
            payment_amount=payment_amount,
        ))
    return {"bookings": result, "total": total, "page": page, "limit": limit}

# GET /stats → Admin: get booking counts and revenue
@router.get("/stats", response_model=schemas.BookingStats)
def get_booking_stats(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    booking_crud = crud.BookingsCRUD(db)
    return booking_crud.get_booking_stats()

# GET /{booking_id}/details → Admin: get full booking detail
@router.get("/{booking_id}/details", response_model=schemas.BookingDetailResponse)
def get_booking_detail(
    booking_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin only")
    booking_crud = crud.BookingsCRUD(db)
    data = booking_crud.get_booking_detail(booking_id)
    if not data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    b = data["booking"]
    room = data["room"]
    listing = data["listing"]
    tenant = data["tenant"]
    owner = data["owner"]
    payments = data["payments"]
    history = data["history"]
    payment_status = payments[0].status if payments else None
    payment_method = payments[0].method if payments else None
    payment_amount = payments[0].amount if payments else None
    address = None
    if listing and listing.location_id:
        loc = crud.LocationsCRUD(db).get(listing.location_id)
        if loc:
            address = f"{loc.street or ''}, {loc.barangay or ''}, {loc.city or ''}, {loc.province or ''}".strip(", ")
    payment_responses = [schemas.PaymentsResponse.model_validate(p) for p in payments]
    history_responses = [schemas.BookingHistoryResponse.model_validate(h) for h in history]
    return schemas.BookingDetailResponse(
        booking_id=b.booking_id, user_id=b.user_id, room_id=b.room_id,
        check_in=b.check_in, check_out=b.check_out, status=b.status,
        total_price=b.total_price, notes=b.notes, created_at=b.created_at,
        updated_at=b.updated_at,
        tenant_name=tenant.name if tenant else None,
        tenant_email=tenant.email if tenant else None,
        tenant_phone=tenant.phone if tenant else None,
        account_setup_complete=tenant.account_setup_complete if tenant else None,
        move_in_requested=b.move_in_requested,
        property_name=listing.bh_name if listing else None,
        property_type=listing.property_type if listing else None,
        room_number=room.room_id if room else None,
        room_type=room.room_type if room else None,
        payment_status=payment_status,
        payment_method=payment_method,
        payment_amount=payment_amount,
        payments=payment_responses,
        history=history_responses,
        listing_id=listing.listing_id if listing else None,
        owner_name=owner.name if owner else None,
        property_address=address,
    )

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