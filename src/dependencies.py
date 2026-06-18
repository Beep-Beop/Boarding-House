from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import Callable
from src import database, security, schemas

limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

bearer_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(database.get_db)
) -> schemas.TokenData:
    payload = security.decode_access_token(credentials.credentials, db=db)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None or role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return schemas.TokenData(user_id=int(user_id), role=role)


def require_role(required_role: str) -> Callable:
    def role_checker(current_user: schemas.TokenData = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_role} role"
            )
        return current_user
    return role_checker


def require_ownership(resource_user_id: int, current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != "admin" and current_user.user_id != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource"
        )
    return current_user
