from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database, security

router = APIRouter(prefix="/social", tags=["Social"])

# In-memory storage
reviews_db = []
favorites_db = []

@router.post("/reviews")
async def add_review(
    boardinghouse_id: int,
    user_name: str,
    rating: float,
    comment: str = ""
):
    """Submit a new review for a boarding house"""
    if not (1 <= rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    new_review = {
        "id": len(reviews_db) + 1,
        "boardinghouse_id": boardinghouse_id,
        "user_name": user_name,
        "rating": rating,
        "comment": comment
    }
    reviews_db.append(new_review)
    return {"message": "Review added successfully", "data": new_review}

@router.get("/reviews/{boardinghouse_id}")
async def get_reviews(boardinghouse_id: int):
    """Get all reviews for a specific boarding house"""
    result = [r for r in reviews_db if r["boardinghouse_id"] == boardinghouse_id]
    return {"boardinghouse_id": boardinghouse_id, "reviews": result}

@router.post("/favorites")
async def add_favorite(
    boardinghouse_id: int,
    user_name: str
):
    """Add a boarding house to user's favorites"""
    # Check if already favorited
    exists = any(
        f["user_name"] == user_name and f["boardinghouse_id"] == boardinghouse_id
        for f in favorites_db
    )
    if exists:
        raise HTTPException(status_code=400, detail="Already in favorites")
    
    new_fav = {
        "id": len(favorites_db) + 1,
        "boardinghouse_id": boardinghouse_id,
        "user_name": user_name
    }
    favorites_db.append(new_fav)
    return {"message": "Added to favorites", "data": new_fav}

@router.get("/favorites/{user_name}")
async def get_user_favorites(user_name: str):
    """Get all favorites for a specific user"""
    result = [f for f in favorites_db if f["user_name"] == user_name]
    return {"user_name": user_name, "favorites": result}