from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/", response_model=schemas.RoomsResponse, status_code=status.HTTP_201_CREATED)
def create_room(room: schemas.RoomsCreate, db: Session = Depends(database.get_db)):
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
def update_room(room_id: int, room_update: schemas.RoomUpdate, db: Session = Depends(database.get_db)):
    rooms_crud = crud.RoomsCRUD(db)

    room = rooms_crud.update(room_id, **room_update.model_dump(exclude_unset=True))

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )
    
    return room

@router.get("/listing/{listing_id}", response_model=List[schemas.RoomsResponse])
def get_listing_rooms(listing_id: int, db: Session = Depends(database.get_db)):
    rooms_crud = crud.RoomsCRUD(db)

    rooms = rooms_crud.get_room_by_listing(listing_id=listing_id)

    return rooms