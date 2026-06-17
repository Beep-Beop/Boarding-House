from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

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

    boarding_house = bh_crud.update(listing_id, **boarding_house_update.model_dump(exclude_unset=True))

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

    return bh_crud.get_by_owner(owner_id=owner_id)

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