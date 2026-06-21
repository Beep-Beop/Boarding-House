from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter
from src.models import AdminLogs

router = APIRouter(prefix="/boarding-houses", tags=["Boarding Houses"])

@router.post("/", response_model=schemas.BoardingHouseResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_boarding_house(request: Request, boarding_house: schemas.BoardingHouseCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "owner":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can create listings")

    bh_crud = crud.BoardingHousesCRUD(db)
    user_crud = crud.UsersCRUD(db)

    if not user_crud.get(current_user.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    return bh_crud.create(owner_id=current_user.user_id, **boarding_house.model_dump())


@router.get("/{listing_id}", response_model=schemas.BoardingHouseResponse)
@limiter.limit("60/minute")
def get_boarding_house(request: Request, listing_id: int, db: Session = Depends(database.get_db)):
    bh_crud = crud.BoardingHousesCRUD(db)

    boarding_house = bh_crud.get(listing_id=listing_id)
    if not boarding_house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding house not found"
        )

    # Populate rejection_reason from latest AdminLog
    log = db.query(AdminLogs).filter(
        AdminLogs.target_type == "listing",
        AdminLogs.target_id == listing_id,
        AdminLogs.action.in_(["REJECTED_PERMIT", "BANNED_LISTING"]),
    ).order_by(AdminLogs.performed_at.desc()).first()
    boarding_house.rejection_reason = log.description if log else None

    return boarding_house


@router.patch("/{listing_id}", response_model=schemas.BoardingHouseResponse)
@limiter.limit("5/minute")
def update_boarding_house(request: Request, listing_id: int, boarding_house_update: schemas.BoardingHouseUpdate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    bh_crud = crud.BoardingHousesCRUD(db)

    bh = bh_crud.get(listing_id)
    if not bh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding house not found"
        )

    if current_user.role != "admin" and bh.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this boarding house"
        )

    reason = boarding_house_update.reason
    update_data = boarding_house_update.model_dump(exclude_unset=True)
    update_data.pop("reason", None)

    boarding_house = bh_crud.update(listing_id, **update_data)

    # Create AdminLog + Notification if admin provided a reason
    if current_user.role == "admin" and reason:
        if boarding_house_update.is_verified is False:
            action = "REJECTED_PERMIT"
        elif boarding_house_update.status == "banned":
            action = "BANNED_LISTING"
        elif boarding_house_update.status == "active" and bh.status == "banned":
            action = "RESTORED_LISTING"
        elif boarding_house_update.is_verified is True:
            action = "VERIFIED_PERMIT"
        else:
            action = "ADMIN_UPDATE"

        crud.AdminLogsCRUD(db).create(
            admin_id=current_user.user_id,
            action=action,
            target_type="listing",
            target_id=listing_id,
            description=reason,
        )

        crud.NotificationsCRUD(db).create(
            user_id=bh.owner_id,
            notif_type="system",
            content=f"Listing #{listing_id} {action.replace('_', ' ').title()}: {reason}",
            triggered_by=current_user.user_id,
            reference_type="listing_rejected",
        )

    return boarding_house


@router.get("/owner/{owner_id}", response_model=List[schemas.BoardingHouseResponse])
@limiter.limit("30/minute")
def get_owner_boarding_houses(request: Request, owner_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    bh_crud = crud.BoardingHousesCRUD(db)

    if current_user.role != "admin" and current_user.user_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this owner's listings"
        )

    listings = bh_crud.get_by_owner(owner_id=owner_id)
    # Populate rejection_reason from latest AdminLog for each listing
    if listings:
        listing_ids = [bh.listing_id for bh in listings]
        logs = db.query(AdminLogs).filter(
            AdminLogs.target_type == "listing",
            AdminLogs.target_id.in_(listing_ids),
            AdminLogs.action.in_(["REJECTED_PERMIT", "BANNED_LISTING"]),
        ).order_by(AdminLogs.performed_at.desc()).all()
        seen = set()
        for log in logs:
            if log.target_id not in seen:
                for bh in listings:
                    if bh.listing_id == log.target_id:
                        bh.rejection_reason = log.description
                        break
                seen.add(log.target_id)
    return listings

@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
def delete_boarding_house(request: Request, listing_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    bh_crud = crud.BoardingHousesCRUD(db)

    bh = bh_crud.get(listing_id)
    if not bh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding house not found"
        )

    if current_user.role != "admin" and bh.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this boarding house"
        )

    bh_crud.delete(listing_id)


@router.get("/admin/listings", response_model=List[schemas.AdminListingResponse])
@limiter.limit("30/minute")
def get_admin_listings(request: Request, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    bh_crud = crud.BoardingHousesCRUD(db)
    return bh_crud.get_admin_listings()

@router.get("/feed/dashboard", response_model=List[schemas.DashboardCardResponse])
@limiter.limit("30/minute")
def get_dashboard_feed(request: Request, limit: int = 20, offset: int = 0, db: Session = Depends(database.get_db)):
    bh_crud = crud.BoardingHousesCRUD(db)
    houses = bh_crud.get_dashboard_listings(limit=limit, offset=offset)

    if not houses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active boarding houses found"
        )
    return houses