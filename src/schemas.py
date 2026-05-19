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
    pass

class AmenitiesResponse(AmenitiesBase):
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
    entity_type: Literal['listing', 'room'] = Field(..., examples=['listing'])
    photo_url: str = Field(..., max_length=255)

class PhotoCreate(PhotoBase):
    entity_id: int

class PhotoResponse(PhotoBase):
    photo_id: int
    entity_id: int
    is_primary: bool
    sort_order: int

    class Config:
        from_attributes = True

class AdminLogsBase(BaseModel):
    action: str = Field(..., max_length=255)
    target_type: Literal['listing', 'user', 'report', 'booking'] = Field(..., examples=["listing"])
    description: Optional[str] = None
    
class AdminLogsCreate(AdminLogsBase):
    target_id: int
    ip_address: Optional[str] = Field(None, max_length=45)

class AdminLogsResponse(AdminLogsBase):
    log_id: int
    admin_id: int
    target_id: int
    ip_address: Optional[str]
    performed_at: datetime

    class Config:
        from_attributes = True

class ReportsBase(BaseModel):
    target_type: Literal['listing', 'user', 'review', 'booking'] = Field(..., examples=['listing'])
    reason: str

class ReportsCreate(ReportsBase):
    target_id: int
    reporter_id: int
    reviewed_id: Optional[int] = None

class ReportsResponse(ReportsBase):
    reporter_id: int
    report_id: int
    target_id: int
    status: Literal['pending', 'reviewed', 'resolved', 'dismissed']
    reviewed_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationsBase(BaseModel):
    type: Literal['booking', 'review', 'system', 'favorite'] = Field(..., examples=['booking'])
    reference_type: str = Field(..., max_length=100)
    content: str

class NotificationsCreate(NotificationsBase):
    user_id: int
    triggered_by: Optional[int]

class NotificationsResponse(NotificationsBase):
    notif_id: int
    user_id: int
    triggered_by: Optional[int]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True    

#Second-Level Dependent Tables

