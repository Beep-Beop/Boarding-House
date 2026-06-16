from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/social", tags=["Social"])

@router.post("/reviews", response_model=schemas.ReviewsResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_review(request: Request, review: schemas.ReviewsCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    review_crud = crud.ReviewsCRUD(db)

    return review_crud.create(user_id=current_user.user_id, **review.model_dump())

@router.get("/reviews/listing/{listing_id}", response_model=List[schemas.ReviewsResponse])
def get_listing_reviews(listing_id: int, db: Session = Depends(database.get_db)):
    review_crud = crud.ReviewsCRUD(db)

    return review_crud.get_reviews_by_listing(listing_id=listing_id)

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_review(request: Request, review_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    review_crud = crud.ReviewsCRUD(db)

    deleted = review_crud.delete(review_id=review_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return None