from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import date, datetime, time
from decimal import Decimal

# INDEPENDENT TABLES

# --- USERS ---
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["John Miguel"])
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    role: Literal['student', 'owner', 'admin'] = Field(..., examples=["student"])
    phone: Optional[str] = Field(None, max_length=20, examples=["09491698858"])
    street: Optional[str] = None
    profile_photo: Optional[str] = None
    id_document_url: Optional[str] = None
    date_of_birth: Optional[date] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, examples=["beepboop123"])
    role: Literal['student', 'owner']

class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)
    role: Literal['student', 'owner']
    phone: Optional[str] = Field(None, max_length=20)
    province: str
    city: str
    barangay: str
    street: Optional[str] = None
    date_of_birth: Optional[date] = None


class UserResponse(UserBase):
    user_id: int
    is_verified: bool
    status: Literal['active', 'banned', 'suspended']
    created_at: datetime
    auth_provider: Literal['email', 'google', 'both'] = 'email'

    model_config = ConfigDict(from_attributes=True)

class PublicUserResponse(UserBase):
    """User response that excludes sensitive/internal fields like auth_provider, is_verified, status."""
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    street: Optional[str] = None
    profile_photo: Optional[str] = None
    date_of_birth: Optional[date] = None
    role: Optional[Literal['student', 'owner', 'admin']] = None
    account_setup_complete: Optional[bool] = None
    auth_provider: Optional[Literal['email', 'google', 'both']] = None

class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    password: str = Field(..., min_length=6, examples=["beepboop123"])
    remember_me: bool = False


# --- LOCATION ---
class LocationBase(BaseModel):
    street: Optional[str] = Field(None, max_length=255)
    barangay: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[Decimal] = Field(None, max_digits=10, decimal_places=8)
    longitude: Optional[Decimal] = Field(None, max_digits=11, decimal_places=8)

class LocationCreate(LocationBase):
    province: str = Field(..., max_length=100)
    city: str = Field(..., max_length=100)
    barangay: str = Field(..., max_length=100)
    street: str = Field(..., max_length=255)

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
    property_type: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price_range: Optional[str] = Field(None, max_length=100)
    permit_url: Optional[str] = Field(None, max_length=255)
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

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if hasattr(obj, 'rooms') and obj.rooms:
            prices = [r.price_per_month for r in obj.rooms if r.price_per_month is not None]
            if prices:
                obj.price_range = f"₱{min(prices):,.0f} - ₱{max(prices):,.0f}"
        return super().model_validate(obj, *args, **kwargs)

class BoardingHouseUpdate(BaseModel):
    location_id: Optional[int] = None
    bh_name: Optional[str] = None
    property_type: Optional[str] = None
    description: Optional[str] = None
    price_range: Optional[str] = None
    permit_url: Optional[str] = None
    rules: Optional[str] = None
    min_stay_months: Optional[int] = None
    status: Optional[Literal['active', 'pending', 'banned']] = None
    is_verified: Optional[bool] = None

# --- PHOTOS ---
class PhotoBase(BaseModel):
    entity_type: Literal['listing', 'room'] = Field(..., examples=['listing'])
    photo_url: str = Field(..., max_length=255)

class PhotoCreate(PhotoBase):
    entity_id: int
    is_primary: bool = False
    sort_order: int = 0

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

class UploadResponse(BaseModel):
    url: str
    filename: str

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
    notif_type: Literal['booking', 'review', 'system', 'favorite'] = Field(..., examples=['booking'])
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

class LinkAmenityRequest(BaseModel):
    listing_id: int
    amenity_name: str

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
    q: Optional[str] = Field(None, max_length=200)
    amenity_ids: Optional[List[int]] = None
    limit: int = 20
    offset: int = 0


# --- FAVORITES ---
class FavoritesBase(BaseModel):
    notes: Optional[str] = Field(None, max_length=255)

class FavoritesCreate(FavoritesBase):
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

class BookingAdminResponse(BookingsResponse):
    tenant_name: Optional[str] = None
    tenant_email: Optional[str] = None
    tenant_phone: Optional[str] = None
    property_name: Optional[str] = None
    property_type: Optional[str] = None
    room_number: Optional[int] = None
    room_type: Optional[str] = None
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    payment_amount: Optional[Decimal] = None

class BookingStats(BaseModel):
    total_bookings: int
    pending_count: int
    active_count: int
    cancelled_count: int
    total_revenue: Decimal

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

class BookingDetailResponse(BookingAdminResponse):
    payments: List[PaymentsResponse] = []
    history: List[BookingHistoryResponse] = []
    listing_id: Optional[int] = None
    owner_name: Optional[str] = None
    property_address: Optional[str] = None


# FOURTH-LEVEL DEPENDENT TABLES

# --- REVIEWS ---
class ReviewsBase(BaseModel):
    rating: int = Field(..., ge=1, le=5) 
    comment: Optional[str] = None

class ReviewsCreate(ReviewsBase):
    listing_id: int
    booking_id: Optional[int] = None 

class ReviewsUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewsResponse(ReviewsBase):
    review_id: int
    user_id: int
    listing_id: int
    booking_id: Optional[int]
    created_at: datetime
    is_verified: bool 
    user_name: Optional[str] = None
    user_profile_picture: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class PaymentQueryFilter(BaseModel):
    user_id: int

class PaymentStatusUpdate(BaseModel):
    status: Literal['pending', 'completed', 'failed', 'refunded']


# --- VIEWINGS ---

class ViewingBase(BaseModel):
    scheduled_date: date
    scheduled_time: Optional[time] = None
    notes: Optional[str] = None

class ViewingCreate(ViewingBase):
    listing_id: int

class ViewingResponse(ViewingBase):
    viewing_id: int
    tenant_id: int
    listing_id: int
    status: Literal['pending', 'confirmed', 'completed', 'cancelled']
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ViewingUpdate(BaseModel):
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[time] = None
    status: Optional[Literal['pending', 'confirmed', 'completed', 'cancelled']] = None
    notes: Optional[str] = None


# --- AUTH ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class VerifyResetCodeRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6)

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6)

class AdminCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)

class SendVerificationRequest(BaseModel):
    email: EmailStr

# --- MAINTENANCE ---
class MaintenanceRequestBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: str

class MaintenanceRequestCreate(MaintenanceRequestBase):
    listing_id: int

class MaintenanceRequestUpdate(BaseModel):
    status: Literal['pending', 'in_progress', 'completed']
    resolved_at: Optional[datetime] = None

class MaintenanceRequestResponse(MaintenanceRequestBase):
    request_id: int
    listing_id: int
    tenant_id: int
    status: Literal['pending', 'in_progress', 'completed']
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# -- Dashboard --

class DashboardCardResponse(BaseModel):
    id:int
    name: str
    location: str
    amenities: str
    desc: Optional[str] = None
    photo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AdminListingResponse(BaseModel):
    id: int
    listing_id: int
    name: str
    bh_name: str
    location: str
    amenities: str
    status: str
    is_verified: bool
    permit_url: Optional[str] = None
    photo_url: Optional[str] = None
    desc: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)