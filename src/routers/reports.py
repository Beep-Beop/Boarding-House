from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=schemas.ReportsResponse)
def create_report(report: schemas.ReportsCreate, db: Session = Depends(database.get_db)):
    report_crud = crud.ReportsCRUD(db)

    return report_crud.create(**report.model_dump())

@router.get("/{reporter_id}", response_model=List[schemas.ReportsResponse])
def get_reports(report_id: int, user_id: int, db: Session = Depends(database.get_db)):
    reports_crud = crud.ReportsCRUD(db)

    return reports_crud.get_by_user(user_id, report_id=report_id)

@router.patch("/{reporter_id}", response_model=schemas.ReportsResponse)
def update_report(report_id: int, status: schemas.ReportsUpdate, db: Session = Depends(database.get_db)):
    report_crud = crud.ReportCRUD(db)

    updated_report = report_crud.update(report_id, **status.model_dump(exclude_unset=True))

    if not updated_report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return updated_report