from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from src.models import (Users, Photo, BoardingHouse, Location, 
                        Amenities, Bookings, Reviews, AdminLogs, 
                        Reports, Notifications, Rooms, ListingAmenities,
                        Favorites, Payments, BookingHistory)

# INDEPENDENT TABLES

class UsersCRUD:
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
        """Standardized: Uniform single-record fetch syntax."""
        return self.db.query(Users).filter(Users.user_id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Users:
        return self.db.query(Users).filter(Users.email == email).first()
    
    def update_status(self, user_id: int, new_status: str) -> Users:
        """Architectural Fix: Returns the modified entity rather than a boolean."""
        user = self.get(user_id)
        if user:
            user.status = new_status
            self.db.commit()
            self.db.refresh(user)
        return user
    
    def register(self, name: str, email: str, password: str, role: str,
                 province: str, city: str, barangay: str, phone: str = None,
                 street: str = None, **kwargs) -> Users:
        
        location = self.db.query(Location).filter(
            Location.province == province,
            Location.city == city,
            Location.barangay == barangay
        ).first()

        if not location:
            location = Location(
                province=province,
                city=city,
                barangay=barangay
            )
            self.db.add(location)
            self.db.flush()

        user = Users(
            name=name,
            email=email,
            password=password,
            role=role,
            phone=phone,
            location_id=location.location_id,
            street=street,
            **kwargs
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

class LocationsCRUD:
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
    
    def get_distinct_provinces(self) -> list[str]:
        results = self.db.query(Location.province).filter(Location.province.isnot(None)).distinct().all()
        return [r[0] for r in results]
    
    def get_distinct_cities(self, province_name: str) -> list[str]:
        results = self.db.query(Location.city).filter(
            Location.province == province_name,
            Location.city.isnot(None)
        ).distinct().all()
        return [r[0] for r in results]

    def get_distinct_barangays(self, city_name: str) -> list[str]:
        results = self.db.query(Location.barangay).filter(
            Location.city == city_name,
            Location.barangay.isnot(None)
        ).distinct().all()
        return [r[0] for r in results]
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
    
    def get(self, amenity_id: int) -> Amenities:
        return self.db.query(Amenities).filter(Amenities.amenity_id == amenity_id).first()

    def get_all(self):
        return self.db.query(Amenities).all()
    
# 1st-LEVEL DEPENDENT TABLES

class BoardingHousesCRUD:
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
    
    def update(self, listing_id: int, **kwargs) -> BoardingHouse:
        bh = self.get(listing_id)
        if bh:
            for key, value in kwargs.items():
                if hasattr(bh, key) and value is not None:
                    setattr(bh, key, value)
            self.db.commit()
            self.db.refresh(bh)
        return bh
    
    def search_listings(self, location_id: int = None, min_price: float = None,
                        max_price: float = None, min_stay_months: int = None):
        query = self.db.query(BoardingHouse).filter(BoardingHouse.status == 'active')

        if location_id is not None:
            query = query.filter(BoardingHouse.location_id == location_id)

        if min_stay_months is not None:
            query = query.filter(BoardingHouse.min_stay_months <= min_stay_months)

        if min_price is not None:
            query = query.join(Rooms).filter(Rooms.price_per_month >= min_price)

        if max_price is not None:
            query = query.join(Rooms).filter(Rooms.price_per_month <= max_price)

        return query.distinct().all()
    

class PhotosCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, entity_type: str, entity_id: int, photo_url: str, is_primary=False, sort_order=0) -> Photo:
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

    def get(self, photo_id: int) -> Photo:
        return self.db.query(Photo).filter(Photo.photo_id == photo_id).first()

    def get_photos_for_entity(self, entity_type: str, entity_id: int):
        return self.db.query(Photo).filter(
            Photo.entity_type == entity_type, 
            Photo.entity_id == entity_id
        ).all()
    
    def delete(self, photo_id: int) -> bool:
        photo = self.get(photo_id)
        if photo:
            self.db.delete(photo)
            self.db.commit()
            return True
        return False
    

class AdminLogsCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, admin_id: int, action: str, target_type: str, target_id: int, **kwargs) -> AdminLogs:
        log = AdminLogs(
            admin_id=admin_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            **kwargs
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
    
    def get(self, log_id: int) -> AdminLogs:
        return self.db.query(AdminLogs).filter(AdminLogs.log_id == log_id).first()

    def get_recent(self, limit: int = 50):
        return self.db.query(AdminLogs).order_by(desc(AdminLogs.performed_at)).limit(limit).all()
    

class ReportsCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, reporter_id: int, target_type: str, target_id: int, reason: str, **kwargs) -> Reports:
        # Fixed: Removed Redundant reported_by to match schemas contract cleanly
        reports = Reports(
            reporter_id=reporter_id,
            target_id=target_id,
            target_type=target_type,
            reason=reason,
            status='pending',
            **kwargs
        )
        self.db.add(reports)
        self.db.commit()
        self.db.refresh(reports)
        return reports

    def get(self, report_id: int) -> Reports:
        """Standardized: Converted get_reports to predictable single fetch syntax."""
        return self.db.query(Reports).filter(Reports.report_id == report_id).first()

    def get_pending_reports(self):
        """Plugs Crash: Router endpoint can now cleanly pull pending validation queues."""
        return self.db.query(Reports).filter(Reports.status == 'pending').all()

    def get_reports_by_listing(self, listing_id: int):
        return self.db.query(Reports).filter(
            Reports.target_type == 'listing',
            Reports.target_id == listing_id
        ).all()

    def update_status(self, report_id: int, new_status: str, resolved_by: int) -> Reports:
        """
        State Side Effect Sync: Automatically writes audit trails to the model 
        to ensure data caught at the boundary layer is preserved in the database.
        """
        report = self.get(report_id)
        if report:
            report.status = new_status
            report.resolved_by = resolved_by
            report.resolved_at = func.now() # Auto-stamps database completion time
            self.db.commit()
            self.db.refresh(report)
        return report


class NotificationsCRUD:
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
    
    def get(self, notif_id: int) -> Notifications:
        return self.db.query(Notifications).filter(Notifications.notif_id == notif_id).first()

    def get_user_unread(self, user_id: int):
        return self.db.query(Notifications).filter(Notifications.user_id == user_id, Notifications.is_read == False).all()
    
    def mark_as_read(self, notif_id: int) -> Notifications:
        notif = self.get(notif_id)
        if notif:
            notif.is_read = True
            self.db.commit()
            self.db.refresh(notif)
        return notif
    
# SECOND-LEVEL DEPENDENT TABLES

class RoomsCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, listing_id: int, capacity: int, price_per_month: float, **kwargs) -> Rooms:
        # Fixed: Corrected kwagrs spelling typo in method arguments unpacking
        rooms = Rooms(
            listing_id=listing_id,
            capacity=capacity,
            price_per_month=price_per_month,
            **kwargs
        )
        self.db.add(rooms)
        self.db.commit()
        self.db.refresh(rooms)
        return rooms
    
    def get(self, room_id: int) -> Rooms:
        """Standardized: Replaced get_room with uniform .get()."""
        return self.db.query(Rooms).filter(Rooms.room_id == room_id).first()
    
    def get_room_by_listing(self, listing_id: int, available_only: bool = False):
        query = self.db.query(Rooms).filter(Rooms.listing_id == listing_id)
        if available_only:
            query = query.filter(Rooms.availability == True)
        return query.all()
    
    def update(self, room_id: int, **kwargs) -> Rooms:
        room = self.get(room_id)
        if room:
            for key, value in kwargs.items():
                if hasattr(room, key) and value is not None:
                    setattr(room, key, value)
            self.db.commit()
            self.db.refresh(room)
        return room
    
    def delete(self, room_id: int) -> bool:
        room = self.get(room_id)
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
        
        listing_id_amenity = ListingAmenities(
            listing_id=listing_id,
            amenity_id=amenity_id,
            notes=notes
        )
        self.db.add(listing_id_amenity)
        self.db.commit()
        self.db.refresh(listing_id_amenity)
        return listing_id_amenity
    
    def get(self, lm_id: int) -> ListingAmenities:
        return self.db.query(ListingAmenities).filter(ListingAmenities.lm_id == lm_id).first()

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
            user_id=user_id,
            listing_id=listing_id,
            notes=notes
        )
        self.db.add(new_fav)
        self.db.commit()
        self.db.refresh(new_fav)
        return {"action": "added", "is_favorite": True}
    
    def get_user_favorites(self, user_id: int):
        """Clean Syntax: Fixed get_user_fav abbreviation drift."""
        return self.db.query(Favorites).filter(Favorites.user_id == user_id).all()
    

class BookingsCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, room_id: int, check_in, check_out, total_price: float, notes: str = None, **kwargs) -> Bookings:
        booking = Bookings(
            user_id=user_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            notes=notes,
            status='pending',
            **kwargs
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking
    
    def get(self, booking_id: int) -> Bookings:
        """Standardized: Replaced get_booking with uniform .get()."""
        return self.db.query(Bookings).filter(Bookings.booking_id == booking_id).first()
    
    def get_user_bookings(self, user_id: int):
        """Clean Naming: Fixed plural collection grammar."""
        return self.db.query(Bookings).filter(Bookings.user_id == user_id).all()
    
    def get_room_bookings(self, room_id: int):
        """Clean Naming: Fixed plural collection grammar."""
        return self.db.query(Bookings).filter(Bookings.room_id == room_id).all()
    
    def update_status(self, booking_id: int, new_status: str, changed_by_user_id: int) -> Bookings:
        booking = self.get(booking_id)
        if not booking:
            return None
        
        old_status = booking.status
        booking.status = new_status

        history_entry = BookingHistory(
            booking_id=booking_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by_user_id
        )
        self.db.add(history_entry)
        self.db.commit()
        self.db.refresh(booking)
        return booking
    

# FOURTH-LEVEL DEPENDENT TABLES

class ReviewsCRUD:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, user_id: int, listing_id: int, rating: int, comment: str = None, booking_id: int = None, **kwargs) -> Reviews:
        is_verified = True if booking_id is not None else False

        reviews = Reviews(
            user_id=user_id,
            listing_id=listing_id,
            rating=rating,
            comment=comment,
            booking_id=booking_id,
            is_verified=is_verified,
            **kwargs
        )
        self.db.add(reviews)
        self.db.commit()
        self.db.refresh(reviews)
        return reviews
    
    def get(self, review_id: int) -> Reviews:
        """Standardized: Uniform single-record fetch syntax."""
        return self.db.query(Reviews).filter(Reviews.review_id == review_id).first()
    
    def get_reviews_by_listing(self, listing_id: int):
        return self.db.query(Reviews).filter(
            Reviews.listing_id == listing_id
        ).order_by(Reviews.created_at.desc()).all()
    
    def update(self, review_id: int, **kwargs) -> Reviews:
        review = self.get(review_id)
        if review:
            for key, value in kwargs.items():
                if hasattr(review, key) and value is not None:
                    setattr(review, key, value)
            self.db.commit()
            self.db.refresh(review)
        return review
    
    def delete(self, review_id: int) -> bool:
        review = self.get(review_id)
        if review:
            self.db.delete(review)
            self.db.commit()
            return True
        return False
    

class BookingHistoryCRUD:
    def __init__(self, db: Session):
        self.db = db

    def get_history_by_booking(self, booking_id: int):
        return self.db.query(BookingHistory).filter(
            BookingHistory.booking_id == booking_id
        ).order_by(BookingHistory.changed_at.asc()).all()
    
    def get_changes_by_user(self, changed_by_user_id: int):
        return self.db.query(BookingHistory).filter(
            BookingHistory.changed_by == changed_by_user_id
        ).order_by(BookingHistory.changed_at.desc()).all()
    

class PaymentsCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create(self, booking_id: int, amount: float, method: str, reference_no: str = None, **kwargs) -> Payments:
        payments = Payments(
            booking_id=booking_id,
            amount=amount,
            method=method,
            reference_no=reference_no,
            status='pending',
            **kwargs
        )
        self.db.add(payments)
        self.db.commit()
        self.db.refresh(payments)
        return payments
    
    def get(self, payment_id: int) -> Payments:
        """Standardized: Uniform single-record fetch syntax."""
        return self.db.query(Payments).filter(Payments.payment_id == payment_id).first()
    
    def get_payments_by_booking(self, booking_id: int):
        return self.db.query(Payments).filter(
            Payments.booking_id == booking_id
        ).order_by(Payments.paid_at.desc()).all()
    
    def update_status(self, payment_id: int, new_status: str) -> Payments:
        """
        Regional Localization Logic Side-Effect: Automatically stamps full transaction 
        completion times when transactions transition to 'completed' states.
        """
        payment = self.get(payment_id)
        if payment:
            payment.status = new_status
            if new_status == 'completed':
                payment.paid_at = func.now() # Synchronizes GCash completion audit times safely
            self.db.commit()
            self.db.refresh(payment)
        return payment