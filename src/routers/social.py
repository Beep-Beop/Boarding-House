from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/social", tags=["Social"])

@router.post("/reviews", response_model=schemas.ReviewsResponse, status_code=status.HTTP_201_CREATED)
def create_review(review: schemas.ReviewsCreate, db: Session = Depends(database.get_db)):
    review_crud = crud.ReviewCRUD(db)

    return review_crud.create(**review.model_dump())

@router.get("/reviews/listing/{listing_id}", response_model=List[schemas.ReviewsResponse])
def get_listing_reviews(listing_id: int, db: Session = Depends(database.get_db)):
    review_crud = crud.ReviewCRUD(db)

    return review_crud.get_reviews_by_listing(listing_id=listing_id)

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: int, db: Session = Depends(database.get_db)):
    review_crud = crud.ReviewCRUD(db)

    deleted = review_crud.delete(review_id=review_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return None