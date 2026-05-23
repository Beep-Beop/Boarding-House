# boarding_houses.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/boarding-houses", tags=["Boarding Houses"])

#rename mo nalang instead ng boarding_house_crud to listing_crud since listing talaga sa boardinghouse
@router.post("/", response_model=schemas.BoardingHouseResponse)
def create_boarding_house(
    #should be listing: schemas.BoardingHouseCreate
   listing: schemas.BoardingHouseCreate,
    db: Session = Depends(database.get_db)
):
    listing_crud = crud.BoardingHouseCRUD(db)

    return listing_crud.create(**listing.model_dump()) 


#instead na boarding_house_id listing_id talaga kinukuha mo dyan wala tayong boarding house id you can check sa models.py
@router.get("/{listing_id}", response_model=schemas.BoardingHouseResponse)

#same here since listing talaga should be get_listing()
def read_boarding_house(
    listing_id: int,
    db: Session = Depends(database.get_db)
):
    #same issue listing_crud 
    listing = crud.BoardingHouseCRUD(db).get(listing_id)

    if not listing:
        raise HTTPException(status_code=404, detail="Boarding House Not Found")

    return listing


#Same issue listing_id
@router.patch("/{listing_id}", response_model=schemas.BoardingHouseResponse)

#update_listing_status
def update_boarding_house(
    #listing_id
    listing_id: int,
    #listing_update
    boarding_house: schemas.BoardingHouseUpdate,
    db: Session = Depends(database.get_db)
):
    #listing_crud
    listing_crud = crud.BoardingHouseCRUD(db)

    if not existing_listing:
        raise HTTPException(status_code=404, detail="Boarding House Not Found")

    #actually this mas nauna dapat to sa error handling pero instead na return gawin mo 
    #nalang variable ex updated_listing = listing_crud.update then so on
    updated_listing = listing_crud.update(
       listing_id,
        **listing_update.model_dump(exclude_unset=True)
    )

    #then return mo nalang ung updtaed listing
    #return updated_listing