from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from typing import Callable, Optional
from src import database, security, schemas

limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

bearer_scheme = HTTPBearer()
bearer_scheme_optional = HTTPBearer(auto_error=False)

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
    
    token_version = payload.get("token_version", 0)
    from src.models import Users
    user = db.query(Users).filter(Users.user_id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Account is {user.status}"
        )
    if user.token_version != token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalidated — you have been logged out from another device"
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


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme_optional),
    db: Session = Depends(database.get_db)
) -> Optional[schemas.TokenData]:
    if credentials is None:
        return None
    payload = security.decode_access_token(credentials.credentials, db=db)
    if payload is None:
        return None
    user_id = payload.get("sub")
    role = payload.get("role")
    if user_id is None or role is None:
        return None
    token_version = payload.get("token_version", 0)
    from src.models import Users
    user = db.query(Users).filter(Users.user_id == int(user_id)).first()
    if not user or user.status != "active" or user.token_version != token_version:
        return None
    return schemas.TokenData(user_id=int(user_id), role=role)
