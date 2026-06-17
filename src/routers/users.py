from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from src import crud, schemas, database, security
from src.dependencies import get_current_user, require_role, limiter
from src.logger import logger

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def create_user(request: Request, user: schemas.UserRegister, db: Session = Depends(database.get_db)):
    try:
        user_crud = crud.UsersCRUD(db)

        existing = user_crud.get_user_by_email(user.email)
        if existing:
            if existing.auth_provider in ("google", "both"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This email is already linked to Google. Please sign in with Google instead."
                )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user_data = user.model_dump()
        user_data["password"] = security.get_password_hash(user_data["password"])
    
        return user_crud.register(**user_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Register error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.get("/", response_model=List[schemas.UserResponse])
@limiter.limit("30/minute")
def list_users(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: schemas.TokenData = Depends(require_role("admin"))
):
    """Admin-only: Returns all registered users."""
    return crud.UsersCRUD(db).get_all()

@router.get("/check-email")
@limiter.limit("30/minute")
def check_email(request: Request, email: str, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)

    existing = user_crud.get_user_by_email(email)
    if existing:
        return {"exists": True, "detail": "Email already registered", "provider": existing.auth_provider}

    return {"exists": False, "detail": "Email is available"}

@router.get("/{user_id}", response_model=schemas.UserResponse)
@limiter.limit("30/minute")
def get_user(request: Request, user_id: int, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    user_crud = crud.UsersCRUD(db)

    user = user_crud.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if current_user.role != "admin" and current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this user's data"
        )

    return schemas.UserResponse.model_validate(user)

@router.patch("/{user_id}", response_model=schemas.UserResponse)
def update_user(user_id: int, user_update: schemas.UserUpdate, db: Session = Depends(database.get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.user_id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")
    user_crud = crud.UsersCRUD(db)
    user = user_crud.update(user_id, **user_update.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return schemas.UserResponse.model_validate(user)

@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
def update_user_status(user_id: int, new_status: str, db: Session = Depends(database.get_db), admin: schemas.TokenData = Depends(require_role("admin"))):
    user_crud = crud.UsersCRUD(db)

    user = user_crud.update_status(user_id=user_id, new_status=new_status)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return schemas.UserResponse.model_validate(user)