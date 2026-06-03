from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/", response_model=schemas.ReportsResponse, status_code=status.HTTP_201_CREATED)
def create_report(report: schemas.ReportsCreate, db: Session = Depends(database.get_db)):
    reports_crud = crud.ReportsCRUD(db)

    return reports_crud.create(**report.model_dump())


@router.get("/{report_id}", response_model=schemas.ReportsResponse)
def get_report(report_id: int, db: Session = Depends(database.get_db)):
    reports_crud = crud.ReportsCRUD(db)

    report = reports_crud.get(report_id=report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report

@router.patch("/{report_id}", response_model=schemas.ReportsResponse)
def update_report(report_id: int, report_update: schemas.ReportsUpdate, db: Session = Depends(database.get_db)):
    reports_crud = crud.ReportsCRUD(db)

    report = reports_crud.update_status(report_id, **report_update.model_dump(exclude_unset=True))

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return report