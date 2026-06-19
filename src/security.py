import secrets
import uuid
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session

from src.config import settings

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta is None:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    else:
        expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())
    })
    encoded_jwt = jwt.encode(to_encode, settings.ACCESS_SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str, db: Session = None) -> dict:
    try:
        payload = jwt.decode(token, settings.ACCESS_SECRET_KEY, algorithms=[settings.ALGORITHM])
        jti = payload.get("jti")
        if db and jti:
            from src.models import TokenBlacklist
            blacklisted = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first()
            if blacklisted:
                return None
            # Probabilistic cleanup: purge expired blacklist entries with ~1% chance
            if secrets.randbelow(100) == 0:
                from datetime import datetime, timezone
                db.query(TokenBlacklist).filter(TokenBlacklist.expires_at < datetime.now(timezone.utc)).delete()
                db.commit()
        return payload
    except JWTError:
        return None

def create_verification_token() -> str:
    return secrets.token_urlsafe(48)