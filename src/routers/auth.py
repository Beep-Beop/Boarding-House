from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas, database, security

router = APIRouter(prefix="/auth", tags=["'Authentication"])

@router.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user_crud = crud.UserCRUD(db)

    # Fetch the user from the databe using their email
    user = user_crud.get_user_by_email(credentials.email)

    # Verify if they exist and if password match
    if not user or not security.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Imcorrect email or password"
        )
    
    # Prevent banned users from logging in
    if getattr(user, "status", "active") != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.status}"
        )
    
    # Will update to JWT Token later
    return {
        "message": "Login Successful!",
        "user_id": user.user_id,
        "role": user.role,
        "name": user.name
    }