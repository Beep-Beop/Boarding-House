from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import date, datetime
from decimal import Decimal

# INDEPENDENT TABLES (No Foreign Keys Required)

# --- USERS ---
""" Represents students, owners, and admins."""
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, examples=["John Miguel"])
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    role: Literal['student', 'owner', 'admin'] = Field(..., examples=["student"])
    phone: Optional[str] = Field(None, max_length=20, examples=["09491698858"])
    profile_photo: Optional[str] = None
    id_document_url: Optional[str] = None

class UserCreate(UserBase):
    # Passwords are only required when creating an account. 
    # They are NEVER in the Base or Response, so we don't accidentally leak them to the frontend!
    password: str = Field(..., min_length=6, examples=["beepboop123"])

class UserResponse(UserBase):
    # What the API returns when fetching a user profile
    user_id: int
    is_verified: bool
    status: Literal['active', 'banned', 'suspended']
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserLogin(BaseModel):
    email: EmailStr = Field(..., examples=["jmsarmiento0304@gmail.com"])
    password = str = Field(..., min_length=6, examples=["beepboop123"])

# --- LOCATION ---
""" Coordinates and addresses for the boarding houses."""
class LocationBase(BaseModel):
    street: Optional[str] = Field(None, max_length=255)
    barangay: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    province: Optional[str] = Field(None, max_length=100)
    latitude: Optional[Decimal] = Field(None, max_digits=10, decimal_places=8)
    longitude: Optional[Decimal] = Field(None, max_digits=11, decimal_places=8)

class LocationCreate(LocationBase):
    pass # Needs nothing extra to create

class LocationResponse(LocationBase):
    location_id: int

    model_config = ConfigDict(from_attributes=True)

# --- AMENITIES ---
""" The global master-list of all possible features (WiFi, Aircon, Kitchen)."""
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
""" The main listing created by owners."""
class BoardingHouseBase(BaseModel):
    bh_name: str = Field(..., max_length=255)
    description: Optional[str] = None
    price_range: str = Field(..., max_length=100)
    permit_url: str = Field(..., max_length=255)
    rules: Optional[str] = None
    min_stay_months: int = 1

class BoardingHouseCreate(BoardingHouseBase):
    # Frontend must provide the location ID to link the house to the map
    location_id: int 
    # Note: owner_id will be extracted from the logged-in user's token in the API, not sent here.

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
    status: Optional[str] = None

# --- PHOTOS ---
""" Generic photo storage for both Listings AND Rooms"""
class PhotoBase(BaseModel):
    # entity_type tells us if this photo is for a 'listing' or a 'room'
    entity_type: Literal['listing', 'room'] = Field(..., examples=['listing'])
    photo_url: str = Field(..., max_length=255)

class PhotoCreate(PhotoBase):
    # The ID of the specific listing or room it belongs to
    entity_id: int

class PhotoResponse(PhotoBase):
    photo_id: int
    entity_id: int
    is_primary: bool # True if this is the cover photo
    sort_order: int  # Defines display sequence (1st, 2nd, 3rd)

    model_config = ConfigDict(from_attributes=True)

# --- ADMIN LOGS ---
""" Security audit trail to track what admins are doing."""
class AdminLogsBase(BaseModel):
    action: str = Field(..., max_length=255)
    # Generic mapping: target_type tells us WHAT was modified (a user? a listing?)
    target_type: Literal['listing', 'user', 'report', 'booking'] = Field(..., examples=["listing"])
    description: Optional[str] = None
    
class AdminLogsCreate(AdminLogsBase):
    target_id: int # The exact ID of the item modified
    ip_address: Optional[str] = Field(None, max_length=45)

class AdminLogsResponse(AdminLogsBase):
    log_id: int
    admin_id: int
    target_id: int
    ip_address: Optional[str]
    performed_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- REPORTS ---
""" Support tickets raised by users about bad houses/reviews/users."""
class ReportsBase(BaseModel):
    target_type: Literal['listing', 'user', 'review', 'booking'] = Field(..., examples=['listing'])
    reason: str # Why are they reporting this?

class ReportsCreate(ReportsBase):
    target_id: int
    reporter_id: int # The person complaining
    reviewed_id: Optional[int] = None # The admin who takes the ticket (starts empty)

class ReportsResponse(ReportsBase):
    reporter_id: int
    report_id: int
    target_id: int
    status: Literal['pending', 'reviewed', 'resolved', 'dismissed']
    reviewed_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- NOTIFICATIONS ---
""" Alerts sent to users (e.g., Booking Approved, Rent Due)."""
class NotificationsBase(BaseModel):
    type: Literal['booking', 'review', 'system', 'favorite'] = Field(..., examples=['booking'])
    reference_type: Optional[str] = Field(None, max_length=100) # e.g., URL path to redirect user on click
    content: str # The actual alert message

class NotificationsCreate(NotificationsBase):
    user_id: int # Receiver
    triggered_by: Optional[int] = None # Sender (If None, it was an automated system message)

class NotificationsResponse(NotificationsBase):
    notif_id: int
    user_id: int
    triggered_by: Optional[int]
    is_read: bool # For the red notification badge
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)  

class NotificationsUpdate(BaseModel):
    is_read: Optional[bool] = None

# SECOND-LEVEL DEPENDENT TABLES

# --- ROOMS ---
""" Individual rentable units inside a Boarding House."""
class RoomsBase(BaseModel):
    room_type: Optional[str] = Field(None, max_length=100)
    capacity: int = Field(..., ge=1) # Max people allowed
    price_per_month: Decimal = Field(...,ge=0, max_digits=10, decimal_places=2)
    floor_level: Optional[int] = None

class RoomsCreate(RoomsBase):
    listing_id: int # Links the room to the boarding house

class RoomsResponse(RoomsBase):
    room_id: int
    listing_id: int
    availability: bool

    model_config = ConfigDict(from_attributes=True)

class RoomUpdate(BaseModel):
    listing_id: Optional[int] = None
    room_type: Optional[str] = None
    capacity: Optional[int] = None
    price_per_month: Optional[float] = None
    availability: Optional[bool] = None
    Floor_level: Optional[int] = None

# --- LISTING AMENITIES ---
""" The mapping table connecting a Boarding House to the Global Amenities list."""
class ListingAmenitiesBase(BaseModel):
    notes: Optional[str] = Field(None, max_length=255) # e.g., "Aircon is timed from 9PM to 6AM"

class ListingAmenitiesCreate(ListingAmenitiesBase):
    listing_id: int
    amenity_id: int

class ListingAmenitiesResponse(ListingAmenitiesBase):
    lm_id: int
    listing_id: int
    amenity_id: int

    model_config = ConfigDict(from_attributes=True)

# --- FAVORITES ---
""" Wishlist for students to save listings they like."""
class FavoritesBase(BaseModel):
    notes: Optional[str] = Field(None, max_length=255)

class FavoritesCreate(FavoritesBase):
    user_id: int #Will Remove Later
    listing_id: int

class FavoritesResponse(FavoritesBase):
    favorite_id: int
    user_id: int
    listing_id: int
    saved_at: datetime

    model_config = ConfigDict(from_attributes=True)


# THIRD-LEVEL DEPENDENT TABLES

# --- BOOKINGS ---
""" Rent/Reservation records between a Student and a Room."""
class BookingsBase(BaseModel):
    check_in: date
    check_out: date
    total_price: Decimal = Field(..., max_digits=10, decimal_places=2) # Cached price at time of booking
    notes: Optional[str] = None # Special requests from student

class BookingsCreate(BookingsBase):
    user_id: int #Will Remove Later
    room_id: int

class BookingsResponse(BookingsBase):
    booking_id: int
    user_id: int
    room_id: int
    status: Literal['active', 'pending', 'cancelled']
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class BookingUpdate(BookingsBase):
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    payment_status: Optional[str] = None

# FOURTH-LEVEL DEPENDENT TABLES

# --- REVIEWS ---
""" Feedback left by students after a booking."""
class ReviewsBase(BaseModel):
    rating: int = Field(..., ge=1, le=5) # 1 to 5 stars
    comment: Optional[str] = None

class ReviewsCreate(ReviewsBase):
    user_id: int
    listing_id: int
    booking_id: Optional[int] = None # Tied to a booking to prove they stayed there

class ReviewsResponse(ReviewsBase):
    review_id: int
    user_id: int
    listing_id: int
    booking_id: Optional[int]
    created_at: datetime
    is_verified: bool # True if the backend confirms they had a valid booking

    model_config = ConfigDict(from_attributes=True)

# --- BOOKING HISTORY ---
""" An audit trail for bookings to prevent disputes over cancellations/approvals."""
class BookingHistoryBase(BaseModel):
    old_status: Optional[Literal['active', 'pending', 'cancelled']] = Field(None, examples=["active"])
    new_status: Literal['active', 'pending', 'cancelled'] = Field(..., examples=["active"])

class BookingHistoryCreate(BookingHistoryBase):
    booking_id: int
    changed_by: int # The user/owner who clicked the approve/cancel button

class BookingHistoryResponse(BookingHistoryBase):
    history_id: int
    booking_id: int
    changed_by: int
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- PAYMENTS ---
""" Financial records attached to a specific booking."""
class PaymentsBase(BaseModel):
    amount: Decimal = Field(..., max_digits=10, decimal_places=2)
    method: Literal['gcash', 'bank_transfer', 'cash', 'card'] = Field(..., examples=["gcash"])
    paid_at: Optional[datetime] = None # Starts None until the money is confirmed
    reference_no: Optional[str] = Field(None, max_length=100) # e.g., GCash Ref No.

class PaymentsCreate(PaymentsBase):
    booking_id: int

class PaymentsResponse(PaymentsBase):
    payment_id: int
    booking_id: int
    status: Literal['pending', 'completed', 'failed', 'refunded']

    model_config = ConfigDict(from_attributes=True)