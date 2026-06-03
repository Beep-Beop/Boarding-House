from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import date, datetime
from decimal import Decimal

# INDEPENDENT TABLES

# --- USERS ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["John Miguel"])
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    role: Literal['student', 'owner', 'admin'] = Field(..., examples=["student"])
    phone: Optional[str] = Field(None, max_length=20, examples=["09491698858"])
    profile_photo: Optional[str] = None
    id_document_url: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, examples=["beepboop123"])
    role: Literal['student', 'owner', 'admin', 'tenant', 'landlord']

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal['tenant', 'landlord']
    phone: Optional[str] = Field(None, max_length=20)
    province: str
    city: str
    barangay: str
    street: Optional[str] = None


class UserResponse(UserBase):
    user_id: int
    is_verified: bool
    status: Literal['active', 'banned', 'suspended']
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    password: str = Field(..., min_length=6, examples=["beepboop123"])


# --- LOCATION ---
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

    model_config = ConfigDict(from_attributes=True)

class LocationOptionsResponse(BaseModel):
    options: List[str]


# --- AMENITIES ---
class AmenitiesBase(BaseModel):
    amenity_name: str = Field(..., max_length=100)
    icon: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = Field(None, max_length=100)

class AmenitiesCreate(AmenitiesBase):
    pass

class AmenitiesResponse(AmenitiesBase):
    amenity_id: int

    model_config = ConfigDict(from_attributes=True)


# FIRST-LEVEL DEPENDENT TABLES

# --- BOARDING HOUSE ---
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

    model_config = ConfigDict(from_attributes=True)

class BoardingHouseUpdate(BaseModel):
    location_id: Optional[int] = None
    bh_name: Optional[str] = None
    description: Optional[str] = None
    price_range: Optional[str] = None
    permit_url: Optional[str] = None
    rules: Optional[str] = None
    min_stay_months: Optional[int] = None
    status: Optional[Literal['active', 'pending', 'banned']] = None


# --- PHOTOS ---
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

    model_config = ConfigDict(from_attributes=True)

class PhotoUploadMetadata(BaseModel):
    entity_type: Literal['listing', 'room'] = Field(..., examples=['listing'])
    entity_id: int
    is_primary: bool = False
    sort_order: int = 0

# --- ADMIN LOGS ---
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

    model_config = ConfigDict(from_attributes=True)


# --- REPORTS ---
class ReportsBase(BaseModel):
    target_type: Literal['listing', 'user', 'review', 'booking'] = Field(..., examples=['listing'])
    reason: str 

class ReportsCreate(ReportsBase):
    target_id: int
    reporter_id: int  # Fixed: Cleaned up and removed redundant reported_by field
    reviewed_id: Optional[int] = None 

class ReportsUpdate(BaseModel):
    status: Literal['resolved', 'dismissed']
    resolved_by: int

class ReportsResponse(ReportsBase):
    report_id: int
    reporter_id: int
    target_id: int
    status: Literal['pending', 'reviewed', 'resolved', 'dismissed']
    reviewed_id: Optional[int]
    created_at: datetime
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None  # Aligned to handle explicit datetime values cleanly

    model_config = ConfigDict(from_attributes=True)


# --- NOTIFICATIONS ---
class NotificationsBase(BaseModel):
    type: Literal['booking', 'review', 'system', 'favorite'] = Field(..., examples=['booking'])
    reference_type: Optional[str] = Field(None, max_length=100)
    content: str 

class NotificationsCreate(NotificationsBase):
    user_id: int 
    triggered_by: Optional[int] = None 

class NotificationsResponse(NotificationsBase):
    notif_id: int
    user_id: int
    triggered_by: Optional[int]
    is_read: bool 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  

class NotificationsUpdate(BaseModel):
    is_read: Optional[bool] = None


# SECOND-LEVEL DEPENDENT TABLES

# --- ROOMS ---
class RoomsBase(BaseModel):
    room_type: Optional[str] = Field(None, max_length=100)
    capacity: int = Field(..., ge=1)
    price_per_month: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    floor_level: Optional[int] = None

class RoomsCreate(RoomsBase):
    listing_id: int 

class RoomsResponse(RoomsBase):
    room_id: int
    listing_id: int
    availability: bool

    model_config = ConfigDict(from_attributes=True)

class RoomUpdate(BaseModel):
    listing_id: Optional[int] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price_per_month: Optional[Decimal] = None  # Fixed: Standardized to Decimal type safety
    availability: Optional[bool] = None
    floor_level: Optional[int] = None  # Fixed: Lowercase 'f' to resolve hidden hasattr() data drops


# --- LISTING AMENITIES ---
class ListingAmenitiesBase(BaseModel):
    notes: Optional[str] = Field(None, max_length=255) 

class ListingAmenitiesCreate(ListingAmenitiesBase):
    listing_id: int
    amenity_id: int

class ListingAmenitiesResponse(ListingAmenitiesBase):
    lm_id: int
    listing_id: int
    amenity_id: int

    model_config = ConfigDict(from_attributes=True)

class ListingSearchQuery(BaseModel):
    location_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_stay_months: Optional[int] = None


# --- FAVORITES ---
class FavoritesBase(BaseModel):
    notes: Optional[str] = Field(None, max_length=255)

class FavoritesCreate(FavoritesBase):
    user_id: int 
    listing_id: int

class FavoritesResponse(FavoritesBase):
    favorite_id: int
    user_id: int
    listing_id: int
    saved_at: datetime

    model_config = ConfigDict(from_attributes=True)


# THIRD-LEVEL DEPENDENT TABLES

# --- BOOKINGS ---
class BookingsBase(BaseModel):
    check_in: date
    check_out: date
    total_price: Decimal = Field(..., max_digits=10, decimal_places=2) 
    notes: Optional[str] = None 

class BookingsCreate(BookingsBase):
    user_id: int 
    room_id: int

class BookingsResponse(BookingsBase):
    booking_id: int
    user_id: int
    room_id: int
    status: Literal['active', 'pending', 'cancelled']
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingUpdate(BaseModel):  # Fixed: Dropped parent class inheritance to support genuine partial updates
    check_in: Optional[date] = None  # Harmonized with BookingsBase fields
    check_out: Optional[date] = None
    total_price: Optional[Decimal] = None
    status: Optional[Literal['active', 'pending', 'cancelled']] = None  # Enforced precise data bounds
    notes: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status: Literal['active', 'pending', 'cancelled']
    changed_by_user_id: int  # Converted from a loose parameter into an encapsulated field


# FOURTH-LEVEL DEPENDENT TABLES

# --- REVIEWS ---
class ReviewsBase(BaseModel):
    rating: int = Field(..., ge=1, le=5) 
    comment: Optional[str] = None

class ReviewsCreate(ReviewsBase):
    user_id: int
    listing_id: int
    booking_id: Optional[int] = None 

class ReviewsResponse(ReviewsBase):
    review_id: int
    user_id: int
    listing_id: int
    booking_id: Optional[int]
    created_at: datetime
    is_verified: bool 

    model_config = ConfigDict(from_attributes=True)


# --- BOOKING HISTORY ---
class BookingHistoryBase(BaseModel):
    old_status: Optional[Literal['active', 'pending', 'cancelled']] = Field(None, examples=["active"])
    new_status: Literal['active', 'pending', 'cancelled'] = Field(..., examples=["active"])

class BookingHistoryCreate(BookingHistoryBase):
    booking_id: int
    changed_by: int 

class BookingHistoryResponse(BookingHistoryBase):
    history_id: int
    booking_id: int
    changed_by: int
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- PAYMENTS ---
class PaymentsBase(BaseModel):
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    method: Literal['gcash', 'bank_transfer', 'cash', 'card'] = Field(..., examples=["gcash"])
    paid_at: Optional[datetime] = None 
    reference_no: Optional[str] = Field(None, max_length=100) 

class PaymentsCreate(PaymentsBase):
    booking_id: int

class PaymentsResponse(PaymentsBase):
    payment_id: int
    booking_id: int
    amount: Decimal
    method: Literal['gcash', 'bank_transfer', 'cash', 'card']
    paid_at: Optional[datetime]
    reference_no: Optional[str]
    status: Literal['pending', 'completed', 'failed', 'refunded']

    model_config = ConfigDict(from_attributes=True)

class PaymentQueryFilter(BaseModel):
    user_id: int

class PaymentStatusUpdate(BaseModel):
    status: Literal['pending', 'completed', 'failed', 'refunded']