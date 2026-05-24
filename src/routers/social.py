from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/social", tags=["Social & Interactions"])

@router.post("/reviews", response_model=schemas.ReviewsResponse)
def create_review(review: schemas.ReviewsCreate, db: Session = Depends(database.get_db)):
    review_crud = crud.ReviewCRUD(db)
    return review_crud.create(**review.model_dump)

@router.get("/reviews/listing/{listing_id}", response_model=List[schemas.ReportsResponse])
def get_listing_reviews(listing_id: int, db: Session = Depends(database.get_db)):
    review_crud = crud.ReviewCRUD(db)
    return review_crud.get_reviews_by_listing(listing_id)

@router.get("/reviews/user/{user_id}", response_model=List[schemas.ReviewsResponse])
def get_user_reviews(user_id: int, db: Session = Depends(database.get_db)):
    review_crud = crud.ReviewCRUD(db)
    return review_crud.get_review_by_user(user_id)

@router.delete("/reviews/{review_id}")
def delete_review(review_id: int, db: Session = Depends(database.get_db)):
    review_crud = crud.ReportsCRUD(db)

    success = review_crud.delete_review(review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    
    return {"message": "Review deleted successfully"}

# Favorites
@router.post("/favorites", response_model=schemas.FavoritesResponse)
def add_favorite(favorite: schemas.FavoritesCreate, db: Session = Depends(database.get_db)):
    fav_crud = crud.FavoritesCRUD(db)

    try:
        new_fav = fav_crud.add_favorite(user_id=favorite.user_id, listing_id=favorite.listing_id)
        return new_fav
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not add favorite. Have you already favorited this listing?")
    
@router.get("/favorites/user/{user_id}", response_model=List[schemas.FavoritesResponse])
def get_user_favorites(user_id: int, db: Session = Depends(database.get_db)):
    fav_crud = crud.FavoritesCRUD(db)
    return fav_crud.get_user_favorites(user_id)

@router.delete("/favorites/{favorite_id}")
def remove_favorite(favorite_id: int, db: Session = Depends(database.get_db)):
    fav_crud = crud.FavoritesCRUD(db)

    success = fav_crud.remove_favorite(favorite_id)
    if not success:
        raise HTTPException(status_code=404, detail="Favorite not found")
    
    return {"message": "Favorite removed successfully"}