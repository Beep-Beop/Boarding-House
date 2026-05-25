from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=schemas.PaymentsResponse, status_code=status.HTTP_201_CREATED)
def create_payment(payment: schemas.PaymentsCreate, db: Session = Depends(database.get_db)):
    payments_crud = crud.PaymentsCRUD(db)

    return payments_crud.create(**payment.model_dump())


@router.get("/{payment_id}", response_model=schemas.PaymentsResponse)
def get_payment(payment_id: int, query_params: schemas.PaymentQueryFilter = Depends(), db: Session = Depends(database.get_db)):
    payments_crud = crud.PaymentsCRUD(db)
    user_crud = crud.UsersCRUD(db)

    if not user_crud.get(user_id=query_params.user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    payment = payments_crud.get(payment_id=payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment