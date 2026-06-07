from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src import crud, schemas, database, security

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserRegister, db: Session = Depends(database.get_db)):
    try:
        user_crud = crud.UsersCRUD(db)

        if user_crud.get_user_by_email(user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        user_data = user.model_dump()
        user_data["password"] = security.get_password_hash(user_data["password"])
        role_map = {"tenant": "student", "landlord": "owner"}
        user_data["role"] = role_map.get(user_data["role"], user_data["role"])
    
        return user_crud.register(**user_data)
    
    except HTTPException:
        raise
    except Exception as e:
        print("REGISTER ERROR", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/login")
def login(credentials: schemas.UserLogin, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)

    user = user_crud.get_user_by_email(credentials.email)
    if not user or not security.verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {"user_id": user.user_id, "role": user.role, "name": user.name}


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)

    user = user_crud.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

@router.patch("/{user_id}/status", response_model=schemas.UserResponse)
def update_user_status(user_id: int, new_status: str, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)

    user = user_crud.update_status(user_id=user_id, new_status=new_status)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/check-email")
def check_email(email: str, db: Session = Depends(database.get_db)):
    user_crud = crud.UsersCRUD(db)

    if user_crud.get_user_by_email(email):
        return {"exist": True, "detail": "Email already registered"}
    
    return {"exists": False, "detail": "Email is available"}