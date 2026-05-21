from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import bcrypt
from typing import List
from pydantic import BaseModel

from src import models, schemas
from src.database import engine, get_db

app = FastAPI(title="Boarding House Finder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---  Password Security ---
def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)

@app.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)

def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    #Check for existing user
    existing_user = db.query(models.Users).filter(models.Users.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email is already registered")
    
    #Hashed Password
    hashed_pwd = get_password_hash(user.password)

    #Create new User
    new_user = models.Users(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
        role=user.role,
        phone=user.phone
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- Login ---

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
def login_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    
    #Find user by email
    user = db.query(models.Users).filter(models.Users.email == credentials.email).first()
    
    #Verify if user exist
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    #Check if banned
    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail=f"Account is {user.status}"
        )

    #JWT Token later
    return {
        "message": "Login successful!", 
        "user_id": user.user_id, 
        "role": user.role,
        "name": user.name
    }

# --- Boarding House ---
@app.post("/boarding-houses/", response_model=schemas.BoardingHouseResponse)
def create_boarding_house(listing: schemas.BoardingHouseCreate, owner_id: int, db: Session = Depends(get_db)):

    new_listing = models.BoardingHouse(
        owner_id=owner_id, #Will be removed
        location_id=listing.location_id,
        bh_name=listing.bh_name,
        description=listing.description,
        price_range=listing.price_range,
        permit_url=listing.permit_url,
        rules=listing.rules,
        min_stay_months=listing.min_stay_months
    )

    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return new_listing

@app.get("/boarding-houses/", response_model=List[schemas.BoardingHouseResponse])
def get_all_boarding_houses(db: Session = Depends(get_db)):

    listing = db.query(models.BoardingHouse).all()
    return listing