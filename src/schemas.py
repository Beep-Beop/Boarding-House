from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import date, datetime
from decimal import Decimal

#Dependent Tables

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["John Miguel"])
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    role: Literal['student', 'owner', 'admin'] = Field(..., examples=["student"])
    phone: Optional[str] = Field(None, max_length=20, examples=["09491698858"])
    profile_photo: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, examples=["beepboop123"])

class UserResponse(UserBase):
    user_id: int
    is_verified: bool
    status: Literal['active', 'suspended', 'pending']
    created_at: datetime

    class Config:
        from_attributes = True