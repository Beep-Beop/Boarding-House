from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src import crud, schemas, database

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/", response_model=schemas.PaymentsResponse)
def create_payments(payments: schemas.PaymentsCreate, db: Session = Depends(database.get_db)):
    payments_crud = crud.PaymentCRUD(db)

    return payments_crud.create(**payments.model_dump())

@router.get("/payments/{payment_id}", response_model=List[schemas.PaymentsResponse])
def get_payments(payment_id: int, user_id: int, db: Session = Depends(database.get_db)):
    payments_crud = crud.PaymentCRUD(db)

    return payments_crud.get_by_user(user_id, payment_id=payment_id)