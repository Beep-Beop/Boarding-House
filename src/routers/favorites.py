from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post("/toggle")
@limiter.limit("10/minute")
def toggle_favorite(request: Request, fav: schemas.FavoritesCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if not crud.BoardingHousesCRUD(db).get(fav.listing_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return crud.FavoritesCRUD(db).toggle_favorite(user_id=current_user.user_id, listing_id=fav.listing_id, notes=fav.notes)


@router.get("/user/{user_id}", response_model=List[schemas.FavoritesResponse])
@limiter.limit("30/minute")
def get_user_favorites(request: Request, user_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view these favorites"
        )
    return crud.FavoritesCRUD(db).get_user_favorites(user_id=user_id)


@router.get("/user/{user_id}/detailed", response_model=List[schemas.FavoriteDetailResponse])
@limiter.limit("30/minute")
def get_user_favorites_detailed(request: Request, user_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view these favorites"
        )
    return crud.FavoritesCRUD(db).get_user_favorites_detailed(user_id=user_id)
