from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/viewings", tags=["Viewings"])


@router.post("/", response_model=schemas.ViewingResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_viewing(
    request: Request,
    viewing: schemas.ViewingCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role not in ("student", "admin"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students and admins can schedule viewings")

    listing = crud.BoardingHousesCRUD(db).get(viewing.listing_id)
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")

    viewings_crud = crud.ViewingsCRUD(db)
    return viewings_crud.create(
        tenant_id=current_user.user_id,
        listing_id=viewing.listing_id,
        scheduled_date=viewing.scheduled_date,
        scheduled_time=viewing.scheduled_time,
        notes=viewing.notes,
    )


@router.get("/user/{user_id}", response_model=List[schemas.ViewingResponse])
@limiter.limit("30/minute")
def get_user_viewings(
    request: Request,
    user_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return crud.ViewingsCRUD(db).get_user_viewings(tenant_id=user_id)


@router.get("/listing/{listing_id}", response_model=List[schemas.ViewingResponse])
@limiter.limit("30/minute")
def get_listing_viewings(
    request: Request,
    listing_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    return crud.ViewingsCRUD(db).get_listing_viewings(listing_id=listing_id)


@router.patch("/{viewing_id}/status", response_model=schemas.ViewingResponse)
@limiter.limit("10/minute")
def update_viewing_status(
    request: Request,
    viewing_id: int,
    update: schemas.ViewingUpdate,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    viewings_crud = crud.ViewingsCRUD(db)
    viewing = viewings_crud.get(viewing_id)
    if not viewing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viewing not found")

    if current_user.role not in ("admin",) and viewing.tenant_id != current_user.user_id:
        listing = crud.BoardingHousesCRUD(db).get(viewing.listing_id)
        if not listing or (listing.owner_id != current_user.user_id and current_user.role != "admin"):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this viewing")

    return viewings_crud.update(viewing_id, **update.model_dump(exclude_none=True))


@router.delete("/{viewing_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_viewing(
    request: Request,
    viewing_id: int,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user),
):
    viewings_crud = crud.ViewingsCRUD(db)
    viewing = viewings_crud.get(viewing_id)
    if not viewing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Viewing not found")

    if current_user.role != "admin" and viewing.tenant_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this viewing")

    viewings_crud.delete(viewing_id)
