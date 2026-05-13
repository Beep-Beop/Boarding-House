from sqlalchemy import Column, Integer, String, Boolean, Enum, ForeignKey, DECIMAL, Text, DateTime, Date, func
from sqlalchemy.orm import relationship
from src.database import Base

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

class Photo(Base):
    __tablename__ = "PHOTOS"

    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(Enum('listing', 'room'), nullable=False)
    entity_id = Column(Integer, nullable=False)
    photo_url = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)