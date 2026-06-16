from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/", response_model=schemas.RoomsResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_room(request: Request, room: schemas.RoomsCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    bh_crud = crud.BoardingHousesCRUD(db)
    bh = bh_crud.get(room.listing_id)
    if not bh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    if bh.owner_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add rooms to this listing")

    rooms_crud = crud.RoomsCRUD(db)
    return rooms_crud.create(**room.model_dump())

@router.get("/{room_id}", response_model=schemas.RoomsResponse)
def get_room(room_id: int, db: Session = Depends(database.get_db)):
    rooms_crud = crud.RoomsCRUD(db)

    room = rooms_crud.get(room_id=room_id)

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    return room


@router.patch("/{room_id}", response_model=schemas.RoomsResponse)
@limiter.limit("10/minute")
def update_room(request: Request, room_id: int, room_update: schemas.RoomUpdate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    rooms_crud = crud.RoomsCRUD(db)

    existing = rooms_crud.get(room_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    bh = crud.BoardingHousesCRUD(db).get(existing.listing_id)
    if bh and bh.owner_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this room")

    room = rooms_crud.update(room_id, **room_update.model_dump(exclude_unset=True))
    return room

@router.get("/listing/{listing_id}", response_model=List[schemas.RoomsResponse])
def get_listing_rooms(listing_id: int, db: Session = Depends(database.get_db)):
    rooms_crud = crud.RoomsCRUD(db)

    rooms = rooms_crud.get_room_by_listing(listing_id=listing_id)

    return rooms