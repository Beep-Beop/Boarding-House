from sqlalchemy.orm import Session
from src.models import (Users, Photo, BoardingHouse, Location, 
                        Amenities, Bookings, Reviews, AdminLogs, 
                        Reports, Notifications, Rooms, ListingAmenities,
                        Favorites, Payments, BookingHistory)

#Dependent Tables

class UserCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, email: str, password: str, role: str, **kwargs) -> Users:
        user = Users(
            name=name,
            email=email,
            password=password,
            role=role,
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get(self, user_id: int) -> Users:
        return self.db.query(Users).filter(Users.user_id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Users:
        return self.db.query(Users).filter(Users.email == email).first()
    
    def update_status(self, user_id: int, new_status: str) -> bool:
        user = self.get(user_id)
        if user:
            user.status = new_status
            self.db.commit()
            return True
        return False

class LocationCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs) -> Location:
        location = Location(**kwargs)
        self.db.add(location)
        self.db.commit()
        self.db.refresh(location) 
        return location
    
    def get(self, location_id: int) -> Location:
        return self.db.query(Location).filter(Location.location_id == location_id).first()
    
class AmenitiesCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, amenity_name: str, icon: str, category: str) -> Amenities:
        amenity = Amenities(
            amenity_name=amenity_name,
            icon=icon,
            category=category
        )
        self.db.add(amenity)
        self.db.commit()
        self.db.refresh(amenity)
        return amenity
    
    def get_all(self):
        return self.db.query(Amenities).all()
    
#1st-Level Dependent Tables

class PhotoCRUD:
    def __init__(self, db: Session):
        self.db = db

    def add_photo(self, entity_type, entity_id, photo_url, is_primary=False, sort_order=0):
        new_photo = Photo(
            entity_type=entity_type,
            entity_id=entity_id,
            photo_url=photo_url,
            is_primary=is_primary,
            sort_order=sort_order
        )
        self.db.add(new_photo)
        self.db.commit()
        self.db.refresh(new_photo)
        return new_photo

    def get_photos_for_entity(self, entity_type: str, entity_id: int):
        return self.db.query(Photo).filter(
            Photo.entity_type == entity_type, 
            Photo.entity_id == entity_id
        ).all()