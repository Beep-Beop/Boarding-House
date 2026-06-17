from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])


@router.post("/", response_model=schemas.MaintenanceRequestResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_maintenance_request(
    request: Request,
    req: schemas.MaintenanceRequestCreate,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    bh = crud.BoardingHousesCRUD(db).get(req.listing_id)
    if not bh:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    maint_crud = crud.MaintenanceCRUD(db)
    return maint_crud.create(listing_id=req.listing_id, tenant_id=current_user.user_id, title=req.title, description=req.description)


@router.get("/listing/{listing_id}", response_model=List[schemas.MaintenanceRequestResponse])
@limiter.limit("30/minute")
def get_listing_maintenance(request: Request, listing_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    maint_crud = crud.MaintenanceCRUD(db)

    bh = crud.BoardingHousesCRUD(db).get(listing_id)
    if not bh:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listing not found"
        )

    # Allow: admin, listing owner, or tenant who created a request for this listing
    if current_user.role != "admin" and bh.owner_id != current_user.user_id:
        # Check if the current user is a tenant with a maintenance request for this listing
        tenant_requests = maint_crud.get_by_listing(listing_id)
        is_tenant = any(r.tenant_id == current_user.user_id for r in tenant_requests)
        if not is_tenant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view maintenance requests for this listing"
            )
        # If tenant, only show their own requests
        return [r for r in tenant_requests if r.tenant_id == current_user.user_id]

    return maint_crud.get_by_listing(listing_id)


@router.get("/owner/{owner_id}", response_model=List[schemas.MaintenanceRequestResponse])
def get_owner_maintenance(owner_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.user_id != owner_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    maint_crud = crud.MaintenanceCRUD(db)
    return maint_crud.get_by_owner(owner_id)


@router.patch("/{request_id}", response_model=schemas.MaintenanceRequestResponse)
@limiter.limit("10/minute")
def update_maintenance_status(
    request: Request,
    request_id: int,
    update: schemas.MaintenanceRequestUpdate,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(get_current_user)
):
    maint_crud = crud.MaintenanceCRUD(db)
    req = maint_crud.get(request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance request not found")

    bh = crud.BoardingHousesCRUD(db).get(req.listing_id)
    if current_user.role != "admin" and (not bh or bh.owner_id != current_user.user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    resolved_at = datetime.now(timezone.utc) if update.status == "completed" else None
    return maint_crud.update_status(request_id, status=update.status, resolved_at=resolved_at)


@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
def delete_maintenance_request(request: Request, request_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    maint_crud = crud.MaintenanceCRUD(db)
    req = maint_crud.get(request_id)
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Maintenance request not found")
    bh = crud.BoardingHousesCRUD(db).get(req.listing_id)
    if current_user.role != "admin" and (not bh or bh.owner_id != current_user.user_id) and current_user.user_id != req.tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    maint_crud.delete(request_id)
