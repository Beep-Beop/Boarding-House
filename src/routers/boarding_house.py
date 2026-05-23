# boarding_houses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/boarding-houses", tags=["Boarding Houses"])


@router.post("/", response_model=schemas.BoardingHouseResponse)
def create_boarding_house(
    boarding_house: schemas.BoardingHouseCreate,
    db: Session = Depends(database.get_db)
):
    boarding_house_crud = crud.BoardingHouseCRUD(db)

    return boarding_house_crud.create(**boarding_house.model_dump())


@router.get("/{boarding_house_id}", response_model=schemas.BoardingHouseResponse)
def read_boarding_house(
    boarding_house_id: int,
    db: Session = Depends(database.get_db)
):
    boarding_house = crud.BoardingHouseCRUD(db).get(boarding_house_id)

    if not boarding_house:
        raise HTTPException(status_code=404, detail="Boarding House Not Found")

    return boarding_house

@router.patch("/{boarding_house_id}", response_model=schemas.BoardingHouseResponse)
def update_boarding_house(
    boarding_house_id: int,
    boarding_house: schemas.BoardingHouseUpdate,
    db: Session = Depends(database.get_db)
):
    boarding_house_crud = crud.BoardingHouseCRUD(db)

    existing_boarding_house = boarding_house_crud.get(boarding_house_id)

    if not existing_boarding_house:
        raise HTTPException(status_code=404, detail="Boarding House Not Found")

    return boarding_house_crud.update(
        boarding_house_id,
        **boarding_house.model_dump(exclude_unset=True)
    )