from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src import crud, schemas, database
from src.dependencies import get_current_user, limiter

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/", response_model=List[schemas.ReportsResponse])
@limiter.limit("30/minute")
def list_reports(request: Request, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can view all reports")
    return crud.ReportsCRUD(db).get_all()

@router.post("/", response_model=schemas.ReportsResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
def create_report(request: Request, report: schemas.ReportsCreate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    reports_crud = crud.ReportsCRUD(db)

    return reports_crud.create(reporter_id=current_user.user_id, **report.model_dump())


@router.get("/{report_id}", response_model=schemas.ReportsResponse)
@limiter.limit("30/minute")
def get_report(request: Request, report_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    reports_crud = crud.ReportsCRUD(db)

    report = reports_crud.get(report_id=report_id)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    if current_user.role != "admin" and report.reporter_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this report"
        )
    
    return report

@router.patch("/{report_id}", response_model=schemas.ReportsResponse)
@limiter.limit("10/minute")
def update_report(request: Request, report_id: int, report_update: schemas.ReportsUpdate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update report status"
        )

    reports_crud = crud.ReportsCRUD(db)

    update_data = report_update.model_dump(exclude_unset=True)
    reason = update_data.pop("reason", None)

    report = reports_crud.update_status(report_id, **update_data)

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    if reason:
        admin_logs_crud = crud.AdminLogsCRUD(db)
        admin_logs_crud.create(
            admin_id=current_user.user_id,
            action="update_report",
            target_type="report",
            target_id=report_id,
            description=reason
        )

        if report.target_type == "review" and report.reviewed_id:
            notif_crud = crud.NotificationsCRUD(db)
            notif_crud.create(
                user_id=report.reporter_id,
                notif_type="system",
                content=f"Your report (ID: {report_id}) has been {report_update.status}. Reason: {reason}",
                triggered_by=current_user.user_id,
                reference_type=f"report_{report_update.status}"
            )

    return report