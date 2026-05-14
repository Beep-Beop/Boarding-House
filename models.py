from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DECIMAL, Text, DateTime, Date, func
from sqlalchemy.orm import relationship
from src.database import Base


#Independent Table
    #Users (Done)
    #Location (Done)
    #Amenities (Done)

#1st Level Dependent Table
    #Boarding House (Done)
    #Photo (Done)
    #Admin Logs
    #Reports
    #Notification

#2nd Level Dependent Table
    #Rooms
    #Listing Amenities
    #Favorites

#3rd Level Dependent Table
    #Bookings

#4th Level Dependent Table
    #Reviews
    #Booking History
    #Payment


class Users(Base):
    __tablename__ = "USERS"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum('student', 'owner', 'admin'), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    phone = Column(String(20))
    profile_photo = Column(String(255))
    id_document_url = Column(String(255))
    is_verified = Column(Boolean, default=False)
    status = Column(Enum('active', 'banned', 'suspended'), default='active')

class Location(Base):
    __tablename__ = "LOCATION"

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    street = Column(String(255))
    barangay = Column(String(100))
    city = Column(String(100))
    province = Column(String(100))
    latitude = Column(DECIMAL(10, 8))
    longtitude = Column(DECIMAL(11, 8))

class Amenities(Base):
    __tablename__ = "AMENITIES"

    amenity_id = Column(Integer, primary_key=True, autoincrement=True)
    amenity_name = Column(String(100), nullable=False)
    icon = Column(String(255))
    category = Column(String(100))

class Boarding_House(Base):
    __tablename__ = "BOARDING_HOUSE"

    listing_id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("USERS.user_id", ondelete="CASCADE"), nullable=False)
    location_id = Column(Integer, ForeignKey("LOCATION.location_id", ondelete="CASCADE"), nullable=False)
    bh_name = Column(String(255), nullable=False)
    description = Column(Text)
    price_range = Column(String(100))
    status = Column(Enum('active', 'pending', 'banned'), default='pending')
    bh_created_at = Column(DateTime, server_default=func.now())
    is_verified = Column(Boolean, default=False)
    permit_url = Column(String(255))
    min_stay_months = Column(Integer, default=1)
    rules = Column(Text)

class Photo(Base):
    __tablename__ = "PHOTOS"

    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(Enum('listing', 'room'), nullable=False)
    entity_id = Column(Integer, nullable=False)
    photo_url = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)

class Admin_Logs(Base):
    __tablename__ = "ADMIN_LOGS"

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    #admin_id
    action = Column(String(255), nullable=False)
    target_type = Column(Enum('listing', 'user', 'report', 'booking'), nullable=False)
    target_id = Column(Integer, nullable=False)
    description = Column(Text)
    ip_address = Column(String(45))
    performed_at = Column(DateTime, server_default=func.now())

class Reports(Base):
    __tablename__ = "REPORTS"

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    #reporter_id
    #reviewed_id
    target_type = Column(Enum('listing', 'user', 'review', 'booking'), nullable=False)
    target_id = Column(Integer, nullable=False)
    reason = Column(Text)
    status = Column(Enum('pending', 'reviewed', 'resolved', 'dismissed'), default='pending')
    created_at = Column(DateTime, server_default=func.now())

class Notifications(Base):
    __tablename__ = "NOTIFICATIONS"

    notif_id = Column(Integer, primary_key=True, autoincrement=True)
    #user_id
    #triggered_by
    type = Column(Enum('booking', 'review', 'system', 'favorite'), nullable=False)
    content = Column(Text)
    is_read = Column(Boolean, default=False)
    reference_type = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())

class Rooms(Base):
    __tablename__ = "ROOMS"

    room_id = Column(Integer, primary_key=True, autoincrement=True)
    #listing_id
    room_type = Column(String(100))
    capacity = Column(Integer, nullable=False)
    price_per_month = Column(DECIMAL(10,2), nullable=False)
    availability = Column(Boolean, default=True)
    floor_level = Column(Integer)

class Listing_Amenities(Base):
    __tablename__ = "LISTING_AMENITIES"
    
    lm_id = Column(Integer, primary_key=True, autoincrement=True)
    #listing_id
    #amenity_id
    notes = Column (String(255))

class Favorites(Base):
    __tablename__ = "FAVORITES"

    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    #user_id
    #listing_id
    saved_at = Column(DateTime, server_default=func.now())
    notes = Column(String(255))

class Bookings(Base):
    __tablename__ = "BOOKINGS"

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    #user_id
    #room_id
    check_in = Column(Date, nullable=False) 
    check_out = Column(Date, nullable=False)
    status = Column(Enum('active', 'pending', 'cancelled'), default='active')
    total_price =Column(DECIMAL(10,2), nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())

class Reviews(Base):
    __tablename__ = "REVIEWS"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    #user_id
    #listing_id
    #booking_id
    rating = Column(Integer, default=False)
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    is_verified = Column(Boolean, default=False)

class Booking_History(Base):
    __tablename__ = "BOOKING_HISTORY"

    history_id = Column(Integer, primary_key=True, autoincrement=True)
    #booking_id
    old_status = Column(Enum('active', 'pending', 'cancelled'))
    newstatus = Column(Enum('active', 'pending', 'cancelled'), nullable=False)
    changed_at = Column(DateTime, server_default=func.now())
    #changed_by

class Payments(Base):
    __tablename__ = "PAYMENTS"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    #booking_id
    amount = Column(DECIMAL(10,2), nullable=False)
    method = Column(Enum('gcash', 'bank_transfer', 'cash', 'card'), nullable=False)
    status = Column(Enum('pending', 'completed', 'failed', 'refunded'))
    paid_at = Column(DateTime)
    reference_no = Column(String(100))