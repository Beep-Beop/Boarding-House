from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DECIMAL, Text, DateTime, Date, func
from sqlalchemy.orm import relationship
from src.database import Base


#Independent Table
    #Users (Done)
    #Location (Done)
    #Amenities

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