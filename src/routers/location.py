from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas, database, state

router = APIRouter(prefix="/locations", tags=["Locations"])

@router.get("/provinces", response_model=schemas.LocationOptionsResponse)
def get_provinces(db: Session = Depends(database.get_db)):
    if state.province_cache:
        return {"options": state.province_cache}
    
    location_crud = crud.LocationsCRUD(db)
    return {"options": location_crud.get_distinct_provinces}

@router.get("/cities", response_model=schemas.LocationOptionsResponse)
def get_cities(province: str, db: Session = Depends(database.get_db)):
    location_crud = crud.LocationsCRUD(db)

    if not province or not province.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Province parameter cannot be empty"
        )
    
    cities = location_crud.get_distinct_cities(province_name=province)

    return {"options": cities}

@router.get("/barangays", response_model=schemas.LocationOptionsResponse)
def get_barangays(city: str, db: Session = Depends(database.get_db)):
    location_crud = crud.LocationsCRUD(db)

    if not city or not city.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City parameter cannot be empty"
        )
    
    barangays = location_crud.get_distinct_barangays(city_name=city)

    return {"options": barangays}