from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas, database, security

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)

    user = user_crud.get_user_by_email(credentials.email)

    if not user or not security.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}"
        )
    
    return {
        "message": "Login Successful!",
        "user_id": user.user_id,
        "role": user.role,
        "name": user.name
    }