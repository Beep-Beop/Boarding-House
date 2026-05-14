from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DECIMAL, Text, DateTime, Date, func
from sqlalchemy.orm import relationship
from src.database import Base

#Independent Tables


class Users(Base):
    __tablename__ = "USERS"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    role = Column(Enum('student', 'owner', 'admin'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    phone = Column(String(20))
    profile_photo = Column(String(255))
    id_document_url = Column(String(255))
    is_verified = Column(Boolean, default=False)
    status = Column(Enum('active', 'banned', 'suspended'), default='active')

    # Relationships
    boarding_houses = relationship("BoardingHouse", backref="owner", cascade="all, delete-orphan")
    bookings = relationship("Bookings", backref="user", cascade="all, delete-orphan")
    reviews = relationship("Reviews", backref="reviewer", cascade="all, delete-orphan")


class Location(Base):
    __tablename__ = "LOCATION"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    street = Column(String(255))
    barangay = Column(String(100))
    city = Column(String(100))
    province = Column(String(100))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))


class Amenities(Base):
    __tablename__ = "AMENITIES"

    amenity_id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_name = Column(String(100), nullable=False)
    icon = Column(String(255))
    category = Column(String(100))


#First-Level Dependent Tables


class BoardingHouse(Base):
    __tablename__ = "BOARDING_HOUSE"

    listing_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("LOCATION.location_id", ondelete="RESTRICT"), nullable=False)
    bh_name = Column(String(255), nullable=False)
    description = Column(Text)
    price_range = Column(String(100))
    status = Column(Enum('active', 'pending', 'banned'), default='pending')
    bh_created_at = Column(DateTime, server_default=func.now())
    is_verified = Column(Boolean, default=False)
    permit_url = Column(String(255))
    min_stay_months = Column(Integer, default=1)
    rules = Column(Text)

    # Relationships
    location = relationship("Location")
    rooms = relationship("Rooms", backref="boarding_house", cascade="all, delete-orphan")
    listing_amenities = relationship("ListingAmenities", backref="boarding_house", cascade="all, delete-orphan")


class Photo(Base):
    __tablename__ = "PHOTOS"

    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(Enum('listing', 'room'), nullable=False)
    entity_id = Column(Integer, nullable=False)
    photo_url = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)


class AdminLogs(Base):
    __tablename__ = "ADMIN_LOGS"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    action = Column(String(255), nullable=False)
    target_type = Column(Enum('listing', 'user', 'report', 'booking'), nullable=False)
    target_id = Column(Integer, nullable=False)
    description = Column(Text)
    ip_address = Column(String(45))
    performed_at = Column(DateTime, server_default=func.now())


class Reports(Base):
    __tablename__ = "REPORTS"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    reporter_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    reviewed_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="SET NULL"))
    target_type = Column(Enum('listing', 'user', 'review', 'booking'), nullable=False)
    target_id = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(Enum('pending', 'reviewed', 'resolved', 'dismissed'), default='pending')
    created_at = Column(DateTime, server_default=func.now())


class Notifications(Base):
    __tablename__ = "NOTIFICATIONS"

    notif_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    triggered_by = Column(Integer, ForeignKey("USERS.user_id", ondelete="SET NULL"))
    type = Column(Enum('booking', 'review', 'system', 'favorite'), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    reference_type = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())


#Second-Level Dependent Tables


class Rooms(Base):
    __tablename__ = "ROOMS"

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    room_type = Column(String(100))
    capacity = Column(Integer, nullable=False)
    price_per_month = Column(DECIMAL(10, 2), nullable=False)
    availability = Column(Boolean, default=True)
    floor_level = Column(Integer)

    # Relationships
    bookings = relationship("Bookings", backref="room", cascade="all, delete-orphan")


class ListingAmenities(Base):
    __tablename__ = "LISTING_AMENITIES"

    lm_id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    amenity_id = Column(Integer, ForeignKey("AMENITIES.amenity_id", ondelete="CASCADE"), nullable=False)
    notes = Column(String(255))

    # Relationship
    amenity = relationship("Amenities")


class Favorites(Base):
    __tablename__ = "FAVORITES"

    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    saved_at = Column(DateTime, server_default=func.now())
    notes = Column(String(255))


#Third-Level Dependent Tables


class Bookings(Base):
    __tablename__ = "BOOKINGS"

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    room_id = Column(Integer, ForeignKey("ROOMS.room_id", ondelete="CASCADE"), nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    status = Column(Enum('active', 'pending', 'cancelled'), default='pending')
    total_price = Column(DECIMAL(10, 2), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    payments = relationship("Payments", backref="booking", cascade="all, delete-orphan")


#Fourth-Level Dependent Tables


class Reviews(Base):
    __tablename__ = "REVIEWS"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    listing_id = Column(Integer, ForeignKey("BOARDING_HOUSE.listing_id", ondelete="CASCADE"), nullable=False)
    booking_id = Column(Integer, ForeignKey("BOOKINGS.booking_id", ondelete="SET NULL"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    is_verified = Column(Boolean, default=False)


class BookingHistory(Base):
    __tablename__ = "BOOKING_HISTORY"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("BOOKINGS.booking_id", ondelete="CASCADE"), nullable=False)
    old_status = Column(Enum('active', 'pending', 'cancelled'))
    new_status = Column(Enum('active', 'pending', 'cancelled'), nullable=False)
    changed_at = Column(DateTime, server_default=func.now())
    changed_by = Column(Integer, ForeignKey("USERS.user_id", ondelete="RESTRICT"), nullable=False)


class Payments(Base):
    __tablename__ = "PAYMENTS"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(Integer, ForeignKey("BOOKINGS.booking_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    method = Column(Enum('gcash', 'bank_transfer', 'cash', 'card'), nullable=False)
    status = Column(Enum('pending', 'completed', 'failed', 'refunded'), default='pending')
    paid_at = Column(DateTime)
    reference_no = Column(String(100))