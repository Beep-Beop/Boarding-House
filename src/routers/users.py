from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src import crud, schemas, database, security

router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    user_crud = crud.UserCRUD(db)

    if user_crud.get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = user.model_dump()

    hashed_pw = security.get_password_hash(user.password)
    user_dict["password"] = hashed_pw

    return user_crud.create(**user_dict)

@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(database.get_db)):
    user = crud.UserCRUD(db).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
        
    return user