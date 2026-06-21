from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.models import (Users, BoardingHouse, Rooms, Favorites, Bookings, Payments,
                        Viewings, Notifications, Reviews, Reports, MaintenanceRequest,
                        BookingHistory, ListingAmenities)
from src.security import get_password_hash


def seed_full():
    db: Session = SessionLocal()
    try:
        users = {u.email: u for u in db.query(Users).all()}
        houses = db.query(BoardingHouse).all()
        if not houses:
            print("No boarding houses found. Run seed_data.py first.")
            return

        student = users.get("miguel@student.com")
        flora = users.get("flora@gmail.com")
        boyet = users.get("boyet@yahoo.com")
        susan = users.get("susan@gmail.com")
        larry = users.get("larry@yahoo.com")
        if not student:
            student = Users(name="John Miguel", email="miguel@student.com",
                            password=get_password_hash("Student123!"),
                            role="student", is_verified=True, email_verified=True,
                            account_setup_complete=True)
            db.add(student)
            db.commit()
        if not flora:
            flora = Users(name="Tita Flora", email="flora@gmail.com",
                          password=get_password_hash("Flora123!"),
                          role="owner", is_verified=True, email_verified=True,
                          account_setup_complete=True)
            db.add(flora)
            db.commit()

        loc_by_house = {}
        for h in houses:
            loc_by_house[h.listing_id] = h.location_id

        print("Seeding Favorites...")
        for h in houses[:3]:
            existing = db.query(Favorites).filter(
                Favorites.user_id == student.user_id,
                Favorites.listing_id == h.listing_id
            ).first()
            if not existing:
                db.add(Favorites(user_id=student.user_id, listing_id=h.listing_id,
                                 notes="Looks promising!"))

        print("Seeding Bookings...")
        today = date.today()
        booking_configs = [
            {"room_idx": 0, "status": "approved", "ci_offset": -30, "co_offset": 90},
            {"room_idx": 1, "status": "pending", "ci_offset": 7, "co_offset": 37},
            {"room_idx": 2, "status": "active", "ci_offset": -15, "co_offset": 75},
            {"room_idx": 3, "status": "cancelled", "ci_offset": -60, "co_offset": -30},
        ]
        for i, h in enumerate(houses):
            if i >= 4:
                break
            rooms = db.query(Rooms).filter(Rooms.listing_id == h.listing_id).all()
            if not rooms:
                continue
            cfg = booking_configs[i]
            room = rooms[0]
            check_in = today + timedelta(days=cfg["ci_offset"])
            check_out = today + timedelta(days=cfg["co_offset"])
            nights = (check_out - check_in).days
            price = float(room.price_per_month) * (nights / 30) if nights > 0 else float(room.price_per_month)
            existing = db.query(Bookings).filter(
                Bookings.user_id == student.user_id,
                Bookings.room_id == room.room_id
            ).first()
            if not existing:
                booking = Bookings(
                    user_id=student.user_id, room_id=room.room_id,
                    check_in=check_in, check_out=check_out,
                    status=cfg["status"], total_price=round(price, 2),
                    move_in_requested=(cfg["status"] == "active")
                )
                db.add(booking)
                db.flush()
                db.add(BookingHistory(
                    booking_id=booking.booking_id,
                    old_status=None, new_status=cfg["status"],
                    changed_by=flora.user_id
                ))

        print("Seeding Payments...")
        approved_bookings = db.query(Bookings).filter(
            Bookings.user_id == student.user_id,
            Bookings.status.in_(["approved", "active"])
        ).all()
        for b in approved_bookings:
            existing = db.query(Payments).filter(Payments.booking_id == b.booking_id).first()
            if not existing:
                db.add(Payments(
                    booking_id=b.booking_id, tenant_id=student.user_id,
                    amount=b.total_price, method="gcash", status="paid",
                    period_start=b.check_in, period_end=b.check_out,
                    due_date=b.check_in, paid_at=datetime.now(),
                    reference_no=f"REF-{b.booking_id:04d}"
                ))

        print("Seeding Viewings...")
        viewing_date = today + timedelta(days=3)
        existing = db.query(Viewings).filter(
            Viewings.tenant_id == student.user_id,
            Viewings.listing_id == houses[4].listing_id
        ).first()
        if not existing:
            db.add(Viewings(
                tenant_id=student.user_id, listing_id=houses[4].listing_id,
                scheduled_date=viewing_date, scheduled_time=None,
                status="pending", notes="Interested in viewing the room"
            ))
        existing = db.query(Viewings).filter(
            Viewings.tenant_id == student.user_id,
            Viewings.listing_id == houses[5].listing_id
        ).first()
        if not existing:
            db.add(Viewings(
                tenant_id=student.user_id, listing_id=houses[5].listing_id,
                scheduled_date=viewing_date - timedelta(days=1), scheduled_time=None,
                status="confirmed", notes=""
            ))

        print("Seeding Notifications...")
        notif_data = [
            {"type": "booking", "content": "Your booking at Cozy Studio Apartment has been approved!",
             "ref": "booking_approved", "days_ago": 5},
            {"type": "booking", "content": "Move-in request confirmed at Cozy Studio Apartment!",
             "ref": "movein_confirmed", "days_ago": 3},
            {"type": "system", "content": "Welcome to Boarding House Finder! Complete your profile to get started.",
             "ref": "welcome", "days_ago": 10},
            {"type": "favorite", "content": "Executive Student Suites is now available at a lower price!",
             "ref": "price_drop", "days_ago": 1},
        ]
        for nd in notif_data:
            existing = db.query(Notifications).filter(
                Notifications.user_id == student.user_id,
                Notifications.reference_type == nd["ref"],
                Notifications.content == nd["content"]
            ).first()
            if not existing:
                n = Notifications(
                    user_id=student.user_id, triggered_by=None,
                    notif_type=nd["type"], content=nd["content"],
                    reference_type=nd["ref"],
                    created_at=datetime.now() - timedelta(days=nd["days_ago"]),
                    is_read=(nd["days_ago"] > 7)
                )
                db.add(n)

        print("Seeding Reviews...")
        for i, h in enumerate(houses[:2]):
            existing = db.query(Reviews).filter(
                Reviews.user_id == student.user_id,
                Reviews.listing_id == h.listing_id
            ).first()
            if not existing:
                booking = db.query(Bookings).filter(
                    Bookings.user_id == student.user_id,
                    Bookings.status.in_(["approved", "active"])
                ).first()
                db.add(Reviews(
                    user_id=student.user_id, listing_id=h.listing_id,
                    booking_id=booking.booking_id if booking else None,
                    rating=5 if i == 0 else 4,
                    comment="Great place! Very clean and the owner is super nice." if i == 0
                    else "Decent place for the price. Would recommend.",
                    is_verified=True
                ))

        print("Seeding Reports...")
        existing = db.query(Reports).filter(
            Reports.reporter_id == student.user_id,
            Reports.target_type == "listing",
            Reports.target_id == houses[6].listing_id
        ).first()
        if not existing:
            db.add(Reports(
                reporter_id=student.user_id, target_type="listing",
                target_id=houses[6].listing_id,
                reason="The photos don't match the actual room.",
                status="pending"
            ))

        print("Seeding Maintenance Requests...")
        active_booking = db.query(Bookings).filter(
            Bookings.user_id == student.user_id,
            Bookings.status == "active"
        ).first()
        if active_booking:
            room = db.query(Rooms).filter(Rooms.room_id == active_booking.room_id).first()
            if room:
                existing = db.query(MaintenanceRequest).filter(
                    MaintenanceRequest.tenant_id == student.user_id,
                    MaintenanceRequest.listing_id == room.listing_id
                ).first()
                if not existing:
                    db.add(MaintenanceRequest(
                        listing_id=room.listing_id, tenant_id=student.user_id,
                        title="Leaking faucet",
                        description="The bathroom sink faucet has been leaking for 2 days.",
                        status="pending"
                    ))
                    db.add(MaintenanceRequest(
                        listing_id=room.listing_id, tenant_id=student.user_id,
                        title="Broken window lock",
                        description="The window lock in the bedroom is broken and won't close properly.",
                        status="in_progress"
                    ))

        db.commit()
        print("Seed complete! Test data added for all features.")
        print()
        print("Login credentials:")
        print("  Student:  miguel@student.com / Student123!")
        print("  Owner:    flora@gmail.com    / Flora123!")
        print("  Admin:    admin@boardinghouse.com")

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_full()
