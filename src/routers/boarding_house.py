from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

# JWT Auth Later

router = APIRouter(prefix="/boarding-houses", tags=["Boarding Houses"])

@router.post("/", response_model=schemas.BoardingHouseResponse, status_code=status.HTTP_201_CREATED)
def create_boarding_house(owner_id: int, boarding_house: schemas.BoardingHouseCreate, db: Session = Depends(database.get_db)):
    bh_crud = crud.BoardingHousesCRUD(db)
    user_crud = crud.UsersCRUD(db)

    if not user_crud.get(owner_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found"
        )

    return bh_crud.create(owner_id=owner_id, **boarding_house.model_dump())


@router.get("/{listing_id}", response_model=schemas.BoardingHouseResponse)
def get_boarding_house(listing_id: int, db: Session = Depends(database.get_db)):
    bh_crud = crud.BoardingHousesCRUD(db)

    boarding_house = bh_crud.get(listing_id=listing_id)
    if not boarding_house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding house not found"
        )

    return boarding_house


@router.patch("/{listing_id}", response_model=schemas.BoardingHouseResponse)
def update_boarding_house(listing_id: int, boarding_house_update: schemas.BoardingHouseUpdate, db: Session = Depends(database.get_db)):
    bh_crud = crud.BoardingHousesCRUD(db)

    boarding_house = bh_crud.update(listing_id, **boarding_house_update.model_dump(exclude_unset=True))
    if not boarding_house:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boarding house not found"
        )

    return boarding_house


@router.get("/owner/{owner_id}", response_model=List[schemas.BoardingHouseResponse])
def get_owner_boarding_houses(owner_id: int, db: Session = Depends(database.get_db)):
    bh_crud = crud.BoardingHousesCRUD(db)

    return bh_crud.get_by_owner(owner_id=owner_id)