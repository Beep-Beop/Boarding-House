from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DECIMAL, Text, DateTime, Date, func, and_
from sqlalchemy.orm import relationship
from src.database import Base

#          INDEPENDENT TABLES

class Users(Base):
    __tablename__ = "USERS"

    #Gonna add date of birth
    #Location Mapping
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False) # Hashed password
    role = Column(Enum('student', 'owner', 'admin'), nullable=False)
    location_id = Column(Integer, ForeignKey("LOCATION.location_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, server_default=func.now()) 
    phone = Column(String(20))
    profile_photo = Column(String(255)) # URL to R2 Bucket
    id_document_url = Column(String(255)) # URL to uploaded Valid ID in R2 Bucket
    is_verified = Column(Boolean, default=False) # True if Admin approves their ID document
    status = Column(Enum('active', 'banned', 'suspended'), default='active')

    # Relationships: If a user is deleted, delete their houses, bookings, and reviews.
    location = relationship("Location", backref="users")
    boarding_houses = relationship("BoardingHouse", backref="owner", cascade="all, delete-orphan")
    bookings = relationship("Bookings", backref="user", cascade="all, delete-orphan")
    reviews = relationship("Reviews", backref="reviewer", cascade="all, delete-orphan")


class Location(Base):
    """Stores a single, specific address for a user or boarding house listing"""
    __tablename__ = "LOCATION"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    province = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    barangay = Column(String(100), nullable=False)
    street = Column(String(255), nullable=True) # e.g., "123 Sumulong Highway"
    latitude = Column(DECIMAL(10, 8), nullable=True)  
    longitude = Column(DECIMAL(11, 8), nullable=True) 


class Amenities(Base):
    """Global list of available amenities in the system (e.g., WiFi, Aircon, Kitchen)"""
    __tablename__ = "AMENITIES"

    amenity_id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_name = Column(String(100), nullable=False)
    icon = Column(String(255)) # URL or FontAwesome class name (e.g., 'wifi')
    category = Column(String(100)) # e.g., 'Room Feature', 'Security', 'Shared'

#     FIRST-LEVEL DEPENDENT TABLES

class BoardingHouse(Base):
    __tablename__ = "BOARDING_HOUSE"

    listing_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    
    # RESTRICT means you cannot delete a location if a boarding house is using it.
    location_id = Column(Integer, ForeignKey("LOCATION.location_id", ondelete="RESTRICT"), nullable=False)
    
    bh_name = Column(String(255), nullable=False)
    description = Column(Text) 
    price_range = Column(String(100)) # e.g., "3000 - 5000"
    status = Column(Enum('active', 'pending', 'banned'), default='pending')
    bh_created_at = Column(DateTime, server_default=func.now()) 
    is_verified = Column(Boolean, default=False) # Requires Admin to approve physical permits
    permit_url = Column(String(255)) # Uploaded business permit in R2
    min_stay_months = Column(Integer, default=1) # Required minimum contract length
    rules = Column(Text) # Curfew, Visitors allowed, etc.

    # Relationships
    location = relationship("Location")
    rooms = relationship("Rooms", backref="boarding_house", cascade="all, delete-orphan")
    listing_amenities = relationship("ListingAmenities", backref="boarding_house", cascade="all, delete-orphan")
    
    # Polymorphic join mapping listing photo cleanup dynamically 
    photos = relationship(
        "Photo",
        primaryjoin="BoardingHouse.listing_id == Photo.entity_id and Photo.entity_type == 'listing'",
        cascade="all, delete-orphan",
        viewonly=False
    )


class Photo(Base):
    """Stores all photos for both Listings and specific Rooms."""
    __tablename__ = "PHOTOS"

    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(Enum('listing', 'room'), nullable=False, index=True) # "house photo or room photo?"
    entity_id = Column(Integer, nullable=False, index=True) # The ID of the specific house or room
    photo_url = Column(String(255), nullable=False) 
    is_primary = Column(Boolean, default=False) # Flags the "Cover Photo" for a listing
    sort_order = Column(Integer, default=0) # Controls gallery image order (1st, 2nd, 3rd)


class AdminLogs(Base):
    """Audit trail to see exactly what actions an Admin performed."""
    __tablename__ = "ADMIN_LOGS"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    action = Column(String(255), nullable=False) # e.g., "APPROVED_LISTING", "BANNED_USER"
    
    # Generic Foreign Key: Identifies what the admin modified
    target_type = Column(Enum('listing', 'user', 'report', 'booking'), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True) 
    
    description = Column(Text) # Detailed notes about why the admin took the action
    ip_address = Column(String(45)) # Logs admin's IP for security audits
    performed_at = Column(DateTime, server_default=func.now())


class Reports(Base):
    """Tickets created when a user reports a bad listing, a bad review, or another user."""
    __tablename__ = "REPORTS"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False) # Who complained?
    reviewed_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="SET NULL"), nullable=True) # Admin who handled it
    
    # Added to match schema contracts and eliminate data drop vulnerabilities
    resolved_by = Column(Integer, ForeignKey("USERS.user_id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    # Generic Foreign Key: What are they reporting?
    target_type = Column(Enum('listing', 'user', 'review', 'booking'), nullable=False, index=True) 
    target_id = Column(Integer, nullable=False, index=True)
    
    reason = Column(Text, nullable=False) # The actual complaint
    status = Column(Enum('pending', 'reviewed', 'resolved', 'dismissed'), default='pending')
    created_at = Column(DateTime, server_default=func.now())

    # Explicit properties resolving ambiguous target mappings to USERS table
    reporter = relationship("Users", foreign_keys=[reporter_id], backref="filed_reports")
    reviewer = relationship("Users", foreign_keys=[reviewed_id], backref="assigned_reports")
    resolver = relationship("Users", foreign_keys=[resolved_by], backref="resolved_reports")


class Notifications(Base):
    __tablename__ = "NOTIFICATIONS"

    notif_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False) # Receiver
    triggered_by = Column(Integer, ForeignKey("USERS.user_id", ondelete="SET NULL"), nullable=True) # Sender (or None if System)
    
    type = Column(Enum('booking', 'review', 'system', 'favorite'), nullable=False) 
    content = Column(Text, nullable=False) # "Your booking was approved!"
    is_read = Column(Boolean, default=False) # For the unread notification badge
    reference_type = Column(String(100)) # Helps frontend create a hyperlink
    created_at = Column(DateTime, server_default=func.now())

    # Explicit non-ambiguous mappings for matching relational tracks
    recipient = relationship("Users", foreign_keys=[user_id], backref="received_notifications")
    sender = relationship("Users", foreign_keys=[triggered_by], backref="sent_notifications")


#    SECOND-LEVEL DEPENDENT TABLES

class Rooms(Base):
    __tablename__ = "ROOMS"

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    room_type = Column(String(100)) # e.g., 'Single', 'Double Deck', 'Studio'
    capacity = Column(Integer, nullable=False) # Max people allowed
    price_per_month = Column(DECIMAL(10, 2), nullable=False)
    availability = Column(Boolean, default=True) # False if fully booked
    floor_level = Column(Integer) # e.g., 1 (Ground), 2 (2nd Floor)

    # Relationships
    bookings = relationship("Bookings", backref="room", cascade="all, delete-orphan")
    
    # Polymorphic join mapping room photo cleanup dynamically
    photos = relationship(
        "Photo",
        primaryjoin="Rooms.room_id == Photo.entity_id and Photo.entity_type == 'room'",
        cascade="all, delete-orphan",
        viewonly=False
    )


class ListingAmenities(Base):
    """Maps the global amenities to a specific boarding house."""
    __tablename__ = "LISTING_AMENITIES"

    lm_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    amenity_id = Column(Integer, ForeignKey("AMENITIES.amenity_id", ondelete="CASCADE"), nullable=False)
    notes = Column(String(255)) # e.g., "100 Mbps Converge Fiber" or "Curfew at 10PM"

    # Relationship
    amenity = relationship("Amenities")


class Favorites(Base):
    """Wishlist/Saved listings for Students."""
    __tablename__ = "FAVORITES"

    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, server_default=func.now())
    notes = Column(String(255)) # Allows user to leave a private note "Close to campus!"

#     THIRD-LEVEL DEPENDENT TABLES

class Bookings(Base):
    __tablename__ = "BOOKINGS"

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False) # Student
    room_id = Column(Integer, ForeignKey("ROOMS.room_id", ondelete="CASCADE"), nullable=False)
    
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    status = Column(Enum('active', 'pending', 'cancelled'), default='pending')
    total_price = Column(DECIMAL(10, 2), nullable=False) # Cached price in case room rent changes later
    notes = Column(Text) # Special requests by the student
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    payments = relationship("Payments", backref="booking", cascade="all, delete-orphan")

#    FOURTH-LEVEL DEPENDENT TABLES

class Reviews(Base):
    __tablename__ = "REVIEWS"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    
    # SET NULL so if the booking is deleted, the review remains attached to the listing
    booking_id = Column(Integer, ForeignKey("BOOKINGS.booking_id", ondelete="SET NULL"), nullable=True) 
    
    rating = Column(Integer, nullable=False) # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    is_verified = Column(Boolean, default=False) # True if system detects they actually booked and stayed here


class BookingHistory(Base):
    """Tracks status changes of a booking for dispute resolution."""
    __tablename__ = "BOOKING_HISTORY"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("BOOKINGS.booking_id", ondelete="CASCADE"), nullable=False)
    old_status = Column(Enum('active', 'pending', 'cancelled'), nullable=True)
    new_status = Column(Enum('active', 'pending', 'cancelled'), nullable=False)
    changed_at = Column(DateTime, server_default=func.now())
    
    # RESTRICT prevents deleting a user if they manipulated a booking status.
    changed_by = Column(Integer, ForeignKey("USERS.user_id", ondelete="RESTRICT"), nullable=False)


class Payments(Base):
    __tablename__ = "PAYMENTS"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("BOOKINGS.booking_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    method = Column(Enum('gcash', 'bank_transfer', 'cash', 'card'), nullable=False)
    status = Column(Enum('pending', 'completed', 'failed', 'refunded'), default='pending')
    paid_at = Column(DateTime, nullable=True) # Nullable until the payment is confirmed 'completed'
    reference_no = Column(String(100)) # e.g., GCash transaction ID