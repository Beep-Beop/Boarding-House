# boarding_houses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/boarding-houses", tags=["Boarding Houses"])

#rename mo nalang instead ng boarding_house_crud to listing_crud since listing talaga sa boardinghouse
@router.post("/", response_model=schemas.BoardingHouseResponse)
def create_boarding_house(
    #should be listing: schemas.BoardingHouseCreate
    boarding_house: schemas.BoardingHouseCreate,
    db: Session = Depends(database.get_db)
):
    boarding_house_crud = crud.BoardingHouseCRUD(db)

    return boarding_house_crud.create(**boarding_house.model_dump()) 


#instead na boarding_house_id listing_id talaga kinukuha mo dyan wala tayong boarding house id you can check sa models.py
@router.get("/{boarding_house_id}", response_model=schemas.BoardingHouseResponse)

#same here since listing talaga should be get_listing()
def read_boarding_house(
    boarding_house_id: int,
    db: Session = Depends(database.get_db)
):
    #same issue listing_crud 
    boarding_house = crud.BoardingHouseCRUD(db).get(boarding_house_id)

    if not boarding_house:
        raise HTTPException(status_code=404, detail="Boarding House Not Found")

    return boarding_house


#Same issue listing_id
@router.patch("/{boarding_house_id}", response_model=schemas.BoardingHouseResponse)

#update_listing_status
def update_boarding_house(
    #listing_id
    boarding_house_id: int,
    #listing_update
    boarding_house: schemas.BoardingHouseUpdate,
    db: Session = Depends(database.get_db)
):
    #listing_crud
    boarding_house_crud = crud.BoardingHouseCRUD(db)

    #wala tayon boarding_house_id listing_id lang also this is redundant hindi to importante you can remove this
    existing_boarding_house = boarding_house_crud.get(boarding_house_id)

    if not existing_boarding_house:
        raise HTTPException(status_code=404, detail="Boarding House Not Found")

    #actually this mas nauna dapat to sa error handling pero instead na return gawin mo 
    #nalang variable ex updated_listing = listing_crud.update then so on
    return boarding_house_crud.update(
        boarding_house_id,
        **boarding_house.model_dump(exclude_unset=True)
    )

    #then return mo nalang ung updtaed listing
    #return updated_listing