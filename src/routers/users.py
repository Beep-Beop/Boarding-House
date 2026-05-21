from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database

router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    
    user_crud = crud.UserCRUD

    if user_crud.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    return user_crud.create(
        name=user.name,
        email=user.email,
        password=user.password,
        role=user.role
    )

@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.UserCRUD(db).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    return user