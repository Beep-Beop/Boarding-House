from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Literal
from datetime import date, datetime
from decimal import Decimal

#Dependent Tables


#User
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["John Miguel"])
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    role: Literal['student', 'owner', 'admin'] = Field(..., examples=["student"])
    phone: Optional[str] = Field(None, max_length=20, examples=["09491698858"])
    profile_photo: Optional[str] = None
    id_document_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, examples=["beepboop123"])

class UserResponse(UserBase):
    user_id: int
    is_verified: bool
    status: Literal['active', 'banned', 'suspended']
    created_at: datetime

    class Config:
        from_attributes = True

#Location
class LocationBase(BaseModel):
    street: Optional[str] = Field(None, max_length=255)
    barangay: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = Field(None, max_digits=10, decimal_places=8)
    longitude: Optional[Decimal] = Field(None, max_digits=11, decimal_places=8)

class LocationCreate(LocationBase):
    pass

class LocationResponse(LocationBase):
    location_id: int

    class Config:
        from_attributes = True

class AmenitiesBase(BaseModel):
    amenity_name: str = Field(..., max_length=100)
    icon: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)

class AmenitiesCreate(AmenitiesBase):
    amenity_name: str = Field(..., max_length=100)

class AmenitiesResponse(AmenitiesBase):
    amenity_name: str = Field(..., max_length=100)
    amenity_id: int

    class Config:
        from_attributes = True

#First-Level Dependent Tables

class BoardingHouseBase(BaseModel):
    bh_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price_range: str = Field(..., max_length=100)
    permit_url: str = Field(..., max_length=255)
    rules: Optional[str] = None
    min_stay_months: int = 1

class BoardingHouseCreate(BoardingHouseBase):
    location_id: int

class BoardingHouseResponse(BoardingHouseBase):
    listing_id: int
    owner_id: int
    location_id: int
    status: Literal['active', 'pending', 'banned']
    bh_created_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True

class PhotoBase(BaseModel):
    entity_type: Literal['listing', 'room'] = Field(..., examples='listing')
    photo_url: str = Field(..., max_length=255)

class PhotoCreate(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    photo_id: int
    entity_id: int
    is_primary: bool
    sort_order: int

    class Config:
        from_attributes = True

class AdminLogsBase(BaseModel):
    action: str = Field(..., max_length=255)
    target_type: Literal['listing', 'user', 'report', 'booking'] = Field(..., examples="listing")
    description: Optional[str] = None
    
class AdminLogsCreat(AdminLogsBase):
    ip_address: Optional[str] = Field(None, max_length=45)

class AdminLogsResponse(AdminLogsBase):
    log_id: int
    admin_id: int
    performed_at: datetime

    class Config:
        from_attributes = True


#test2345