from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.post("/", response_model=schemas.RoomResponse)
def create_room(room: schemas.RoomsCreate, db: Session = Depends(database.get_db)):
    room_crud = crud.RoomCRUD(db)

    return room_crud.create(**room.model_dump())

@router.patch("/{room_id}", response_model=schemas.RoomResponse)
def update_room(room_id: int, room_update: schemas.RoomUpdate, db: Session = Depends(database.get_db)):
    room_crud = crud.RoomCRUD(db)

    updated_room = room_crud.update(room_id, **room_update.model_dump(exclude_unset=True))

    if not updated_room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return updated_room