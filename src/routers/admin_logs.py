from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src import crud, schemas, database
from src.dependencies import get_current_user, require_role, limiter

router = APIRouter(prefix="/admin-logs", tags=["Admin Logs"])


@router.get("/", response_model=List[schemas.AdminLogsResponse])
@limiter.limit("30/minute")
def get_all_admin_logs(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(require_role("admin")),
):
    logs = crud.AdminLogsCRUD(db).get_recent(limit=50)
    return [schemas.AdminLogsResponse.model_validate(log) for log in logs]


@router.get("/recent", response_model=List[schemas.AdminLogsResponse])
@limiter.limit("30/minute")
def get_recent_admin_logs(
    request: Request,
    limit: int = 5,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(require_role("admin")),
):
    logs = crud.AdminLogsCRUD(db).get_recent(limit=limit)
    return [schemas.AdminLogsResponse.model_validate(log) for log in logs]
