from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter(prefix="/social", tags=["Social"])

# Data models
class Review(BaseModel):
    boardinghouse_id: int
    user_name: str
    rating: float
    comment: str = ""

class Favorite(BaseModel):
    boardinghouse_id: int
    user_name: str

# In-memory storage
reviews_db = []
favorites_db = []

@router.post("/reviews")
async def add_review(review: Review):
    """Submit a new review for a boarding house"""
    if not (1 <= review.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    new_review = review.dict()
    new_review["id"] = len(reviews_db) + 1
    reviews_db.append(new_review)
    return {"message": "Review added successfully", "data": new_review}

@router.get("/reviews/{boardinghouse_id}")
async def get_reviews(boardinghouse_id: int):
    """Get all reviews for a specific boarding house"""
    result = [r for r in reviews_db if r["boardinghouse_id"] == boardinghouse_id]
    return {"boardinghouse_id": boardinghouse_id, "reviews": result}

@router.post("/favorites")
async def add_favorite(favorite: Favorite):
    """Add a boarding house to user's favorites"""
    # Check if already favorited
    exists = any(
        f["user_name"] == favorite.user_name and f["boardinghouse_id"] == favorite.boardinghouse_id
        for f in favorites_db
    )
    if exists:
        raise HTTPException(status_code=400, detail="Already in favorites")
    
    new_fav = favorite.dict()
    new_fav["id"] = len(favorites_db) + 1
    favorites_db.append(new_fav)
    return {"message": "Added to favorites", "data": new_fav}

@router.get("/favorites/{user_name}")
async def get_user_favorites(user_name: str):
    """Get all favorites for a specific user"""
    result = [f for f in favorites_db if f["user_name"] == user_name]
    return {"user_name": user_name, "favorites": result}