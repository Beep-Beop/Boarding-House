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
    
class AdminLogsCreate(AdminLogsBase):
    ip_address: Optional[str] = Field(None, max_length=45)

class AdminLogsResponse(AdminLogsBase):
    log_id: int
    admin_id: int
    performed_at: datetime

    class Config:
        from_attributes = True

class ReportsBase(BaseModel):
    target_type: Literal['listing', 'user', 'review', 'booking'] = Field(..., examples='listing')
    reason: Optional[str]

class ReportsCreate(ReportsBase):
    reporter_id: int
    reviewed_id: int

class ReportsResponse(ReportsBase):
    report_id: int
    target_id: int
    status: Literal['pending', 'reviewd', 'resolved', 'dismissed']
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationsBase(BaseModel):
    type: Literal['booking', 'review', 'system', 'favorite'] = Field(..., examples='booking')
    reference_type: str = Field(None, max_length=100)

class NotificationsCreate(NotificationsBase):
    triggered_by: int

class NotificationsResponse(NotificationsBase):
    notif_id: int
    user_id: int
    content: Optional[str]
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True    

#Second-Level Dependent Tables

class RoomsBase(BaseModel):
    room_type: str = Field(None, max_length=100)
    capacity: int
    price_per_month: Optional[Decimal] = Field(..., max_digits=10, decimal_places=2)
    floor_level: int

class RoomsCreate(RoomsBase):
    listing_id: int

class RoomsResponse(RoomsBase):
    room_id: int
    availability: bool

    class Config:
        from_attributes = True

class ListingAmenitiesBase(BaseModel):
    notes: str = Field(None, max_length=255)

class ListingAmenitiesCreate(ListingAmenitiesBase):
    listing_id: int
    amenity_id: int

class ListingAmenitiesResponse(ListingAmenitiesBase):
    lm_id: int

    class Config:
        from_attributes = True

class FavoritesBase(BaseModel):
    notes: str = Field(None, max_length=255)

class FavoritesCreate(FavoritesBase):
    user_id: int
    listing_id: int

class FavoritesResponse(FavoritesBase):
    favorite_id: int
    saved_at: datetime

    class Config:
        from_attributes = True

#Third-Level Dependent Tables

class BookingsBase(BaseModel):
    check_in: date
    check_out: date
    total_price: Optional[Decimal] = Field(..., max_digits=10, decimal_places=2)
    notes: Optional[str]

class BookingsCreate(BookingsBase):
    user_id: int
    room_id: int

class BookingsResponse(BookingsBase):
    booking_id: int
    status: Literal['active', 'pending', 'cancelled']
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

#Fourth-Level Dependent Tables

class ReviewsBase(BaseModel):
    rating: int
    comment: Optional[str]

class ReviewsCreate(ReviewsBase):
    user_id: int
    listing_id: int
    booking_id: int

class ReviewsResponse(ReviewsBase):
    review_id: int
    created_at: datetime
    is_verified: bool

    class Config:
        from_attributes = True

class BookingHistoryBase(BaseModel):
    old_status: Literal['active', 'pending', 'cancelled'] = Field(None, examples="active")
    new_status: Literal['active', 'pending', 'cancelled'] = Field(..., examples="active")

class BookingHistoryCreate(BookingHistoryBase):
    booking_id: int
    changed_by: int

class BookingHistoryResponse(BookingHistoryBase):
    history_id: int
    changed_at: datetime

    class Config:
        from_attributes = True

class PaymentsBase(BaseModel):
    amount: Optional[Decimal] = Field(..., max_digits=10, decimal_places=2)
    method: Literal['gcash', 'bank_transfer', 'cash', 'card'] = Field(..., examples="gcash")
    paid_at: datetime
    reference_no: str = Field(None, max_length=100)

class PaymentsCreate(PaymentsBase):
    booking_id: int

class PaymentsResponse(PaymentsBase):
    payment_id: int
    status: Literal['pending', 'completed', 'failed', 'refunded']

    class Config:
        from_attributes = True