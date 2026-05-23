# rooms.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.patch("/{room_id}", response_model=schemas.RoomResponse)
def update_room(
    room_id: int,
    room: schemas.RoomUpdate,
    db: Session = Depends(database.get_db)
):
    room_crud = crud.RoomCRUD(db)

    existing_room = room_crud.get(room_id)

    if not existing_room:
        raise HTTPException(status_code=404, detail="Room Not Found")

    return room_crud.update(
        room_id,
        **room.model_dump(exclude_unset=True)
    )