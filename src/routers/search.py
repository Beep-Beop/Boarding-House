from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/", response_model=List[schemas.BoardingHouseResponse])
def get_search_results(search_filters: schemas.ListingSearchQuery = Depends(), db: Session = Depends(database.get_db)):
    listing_crud = crud.BoardingHousesCRUD(db)

    if search_filters.min_price and search_filters.max_price:
        if search_filters.min_price > search_filters.max_price:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Minimum price threshold cannot exceed the maximum price limit"
            )

    results = listing_crud.search_listings(**search_filters.model_dump(exclude_none=True))

    return results