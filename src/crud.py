from sqlalchemy.orm import Session
from sqlalchemy import desc
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

    def create(self, amenity_name: str, **kwargs) -> Amenities:
        amenity = Amenities(
            amenity_name=amenity_name,
            **kwargs
        )
        self.db.add(amenity)
        self.db.commit()
        self.db.refresh(amenity)
        return amenity
    
    def get_all(self):
        return self.db.query(Amenities).all()
    
#1st-Level Dependent Tables

class BoardingHouseCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, owner_id: int, location_id: int, bh_name: str, **kwargs) -> BoardingHouse:
        bh = BoardingHouse(
            owner_id=owner_id,
            location_id=location_id,
            bh_name=bh_name,
            **kwargs
        )
        self.db.add(bh)
        self.db.commit()
        self.db.refresh(bh)
        return bh
    
    def get(self, listing_id: int) -> BoardingHouse:
        return self.db.query(BoardingHouse).filter(BoardingHouse.listing_id == listing_id).first()
    
    def get_by_owner(self, owner_id: int):
        return self.db.query(BoardingHouse).filter(BoardingHouse.owner_id == owner_id).all()
    
    def update_status(self, listing_id: int, status: str) -> bool:
        bh = self.get(listing_id)
        if bh:
            bh.status = status
            self.db.commit()
            return True
        return False
        

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
    
class AdminLogCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, admin_id: int, action: str, target_type: str, target_id: int, **kwargs) -> AdminLogs:
        log = AdminLogs(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id
            **kwargs
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get_recent(self, limit: int = 50):
        return self.db.query(AdminLogs).order_by(desc(AdminLogs.performed_at)).limit(limit).all()
    
class ReportsCRUD:
    def __init__(self, db:Session):
        self.db = db

    def create(self, reporter_id: int, reviewed_id: int, target_type: str, target_id: int, reason: str, **kwargs) -> Reports:
        reports = Reports(
            reporter_id=reporter_id,
            reviewed_id=reviewed_id,
            target_id=target_id,
            target_type=target_type,
            reason=reason,
            **kwargs
        )
        self.db.add(reports)
        self.db.commit()
        self.db.refresh(reports)
        return reports

    #Specific report
    def get_reports(self, report_id: int):
        return self.db.query(Reports).filter(Reports.report_id == report_id).first()

    #All of the complaints against a specific baording house
    def get_reports_by_listing(self, listing_id: int):
        return self.db.query(Reports).filter(
            Reports.target_type == 'listing',
            Reports.target_id == listing_id
        ).all()

    def update_status(self, report_id: int, new_status: str) -> bool:
        report = self.get_reports(report_id)

        if report:
            report.status = new_status
            self.db.commit()
            return True
        return False

class NotificationCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, type: str, content: str, **kwargs) -> Notifications:
        notif = Notifications(
            user_id=user_id,
            type=type,
            content=content,
            **kwargs
        )
        self.db.add(notif)
        self.db.commit()
        self.db.refresh(notif)
        return notif
    
    def get_user_unread(self, user_id: int):
        return self.db.query(Notifications).filter(Notifications.user_id == user_id, Notifications.is_read == False).all()
    
    def mark_as_read(self, notif_id: int) -> bool:
        notif = self.db.query(Notifications).filter(Notifications.notif_id == notif_id).first()
        if notif:
            notif.is_read = True
            self.db.commit()
            return True
        return False
    
#Second-Level Dependent Tables

class RoomsCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, listing_id: int, capacity: int, price_per_month: float, **kwagrs) -> Rooms:
        rooms = Rooms(
            listing_id=listing_id,
            capacity=capacity,
            price_per_month=price_per_month,
            **kwagrs
        )
        self.db.add(rooms)
        self.db.commit()
        self.db.refresh(rooms)
        return rooms
    
    def get_room(self, room_id: int):
        return self.db.query(Rooms).filter(Rooms.room_id == room_id).first()
    
    def get_room_by_listing(self, listing_id: int, available_only: bool = False):
        query =  self.db.query(Rooms).filter(Rooms.listing_id == listing_id)
        if available_only:
            query = query.filter(Rooms.availability == True)
            
        return query.all()
    
    def update(self, room_id: int, **kwargs) -> bool:
        room = self.get_room(room_id)
        if not room:
            return False
        
        for key, value in kwargs.items():
            if hasattr(room, key) and value is not None:
                setattr(room, key, value)
        
        self.db.commit()
        return True
    
    def delete(self, room_id: int) -> bool:
        room = self.get_room(room_id)
        if room:
            self.db.delete(room)
            self.db.commit()
            return True
        return False
    
class ListingAmenitiesCRUD:
    def __init__(self, db: Session):
        self.db = db

    def add_amenities_to_listing(self, listing_id: int, amenity_id: int, notes: str = None) -> ListingAmenities:
        exists = self.db.query(ListingAmenities).filter(
            ListingAmenities.listing_id == listing_id,
            ListingAmenities.amenity_id == amenity_id
        ).first()

        if exists:
            return exists
        
        listing_amenity = ListingAmenities(
            listing_id=listing_id,
            amenity_id=amenity_id,
            notes=notes
        )
        self.db.add(listing_amenity)
        self.db.commit()
        self.db.refresh(listing_amenity)
        return listing_amenity
    
    def get_amenities_by_listing(self, listing_id: int):
        return self.db.query(ListingAmenities).filter(ListingAmenities.listing_id == listing_id).all()
    
    def remove_amenity_from_listing(self, listing_id: int, amenity_id: int) -> bool:
        item = self.db.query(ListingAmenities).filter(
            ListingAmenities.listing_id == listing_id,
            ListingAmenities.amenity_id == amenity_id
        ).first()

        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False
    
class FavoritesCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def toggle_favorite(self, user_id: int, listing_id: int, notes: str = None) -> dict:
        existing_fav = self.db.query(Favorites).filter(
            Favorites.user_id == user_id,
            Favorites.listing_id == listing_id
        ).first()

        if existing_fav:
            self.db.delete(existing_fav)
            self.db.commit()
            return {"action": "removed", "is_favorite": False}
        
        new_fav = Favorites(
            user_id==user_id,
            listing_id==listing_id,
            notes==notes
        )
        self.db.add(new_fav)
        self.db.commit()
        self.db.refresh(new_fav)
        return {"action": "added", "is_favorite": True}
    
    def get_user_fav(self, user_id: int):
        return self.db.query(Favorites).filter(Favorites.user_id == user_id).first()
    
class BookingsCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, room_id: int, check_in, check_out, total_price: float, notes: str = None, *kwargs) ->Bookings:
        booking = Bookings(
            user_id=user_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            notes=notes,
            **kwargs,
            status='pending'
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
    
    def get_booking(self, booking_id: int):
        return self.db.query(Bookings).filter(Bookings.booking_id == booking_id).first()
    
    def get_user_booking(self, user_id: int):
        return self.db.query(Bookings).filter(Bookings.user_id == user_id).all()
    
    def get_room_booking(self, room_id: int):
        return self.db.query(Bookings).filter(Bookings.room_id == room_id).all()
    
    def update_status(self, booking_id: int, new_status: str, changed_by_user_id: int) ->bool:
        booking = self.get_booking(booking_id)
        if not booking:
            return False
        
        old_status = booking_status
        booking_status = new_status

        history_entry = BookingHistory(
            booking_id=booking_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_user_id=changed_by_user_id
        )
        self.db.add(history_entry)
        self.db.commit()
        return True

    

        