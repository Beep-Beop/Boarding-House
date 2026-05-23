# boarding_houses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/listings", tags=["BoardingHouses"])

@router.post("/", response_model=schemas.BoardingHouseResponse)
def create_boarding_house(listing: schemas.BoardingHouseCreate, db: Session = Depends(database.get_db)):
    listing_crud = crud.BoardingHouseCRUD(db)

    return listing_crud.create(**listing.model_dump()) 

@router.get("/{listing_id}", response_model=schemas.BoardingHouseResponse)

def get_listing(listing_id: int, db: Session = Depends(database.get_db)):
    listing_crud = crud.BoardingHouseCRUD(db).get(listing_id)

    listing = listing_crud(listing_id)

    if not listing:
        raise HTTPException(status_code=404, detail="Boarding House Not Found")

    return listing


@router.patch("/{listing_id}", response_model=schemas.BoardingHouseResponse)

def update_listing_status(listing_id: int, listing_update: schemas.BoardingHouseUpdate, db: Session = Depends(database.get_db)):
    listing_crud = crud.BoardingHouseCRUD(db)

    update_listing = listing_crud.update(listing_id, **listing_update.model_dump(exclude_unset=True))

    if not update_listing:
        raise HTTPException(status_code=404, detail="Boarding house no found")

    return update_listing