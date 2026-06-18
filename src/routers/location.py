from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/", response_model=schemas.LocationResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_location(request: Request, location: schemas.LocationCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    location_crud = crud.LocationsCRUD(db)
    result = location_crud.create(**location.model_dump())
    cache = request.app.state.cache
    cache.invalidate_provinces()
    return result

@router.get("/provinces", response_model=schemas.LocationOptionsResponse)
@limiter.limit("30/minute")
def get_provinces(request: Request, db: Session = Depends(database.get_db)):
    cache = request.app.state.cache
    if cache.is_province_cached():
        return {"options": cache.get_provinces()}

    location_crud = crud.LocationsCRUD(db)
    provinces = location_crud.get_distinct_provinces()
    cache.set_provinces(provinces)
    return {"options": provinces}

@router.get("/cities", response_model=schemas.LocationOptionsResponse)
@limiter.limit("30/minute")
def get_cities(request: Request, province: str, db: Session = Depends(database.get_db)):
    location_crud = crud.LocationsCRUD(db)

    if not province or not province.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Province parameter cannot be empty"
        )
    
    provinces = location_crud.get_distinct_provinces()
    if not any(p.lower() == province.lower() for p in provinces):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Province not found"
        )

    cities = location_crud.get_distinct_cities(province_name=province)

    return {"options": cities}

@router.get("/barangays", response_model=schemas.LocationOptionsResponse)
@limiter.limit("30/minute")
def get_barangays(request: Request, city: str, db: Session = Depends(database.get_db)):
    location_crud = crud.LocationsCRUD(db)

    if not city or not city.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City parameter cannot be empty"
        )
    
    if not location_crud.city_exists(city):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found"
        )

    barangays = location_crud.get_distinct_barangays(city_name=city)

    return {"options": barangays}