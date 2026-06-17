import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.database import SessionLocal
from src.models import Users
from src.security import get_password_hash


def create_admin():
    db = SessionLocal()
    try:
        admin = Users(
            name="System Admin",
            email="admin@boardinghouse.com",
            password=get_password_hash("Admin123!"),
            role="admin",
            email_verified=True,
            account_setup_complete=True,
            status="active",
            auth_provider="email",
        )
        db.add(admin)
        db.commit()
        print("Admin created: admin@boardinghouse.com / Admin123!")
    except Exception as e:
        db.rollback()
        print(f"Error (admin may already exist): {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
