from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from src import schemas, database, models

router = APIRouter(prefix="/search", tags=['Search'])

@router.get("/", response_model=List[schemas.BoardingHouseResponse])
def search_boarding_houses(
    location: Optional[str] = Query(None, description="Search by city or barangay"),
    db: Session = Depends(database.get_db)
):
    
    query = db.query(models.BoardingHouse).filter(models.BoardingHouse.status == 'active')

    if location:
        query = query.join(models.Location).filter(
            (models.Location.city.ilike(f"%{location}%")) |
            (models.Location.barangay.ilike(f"%{location}%"))
        )

    results = query.all()
    return results