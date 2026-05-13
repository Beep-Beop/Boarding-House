from sqlalchemy.orm import Session
from src.models import Users, Photo

class UserCRUD:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, name, email, password, role, **kwargs):
        new_user = Users(
            name=name, 
            email=email, 
            password=password, 
            role=role,
            **kwargs
        )
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def get_user_by_email(self, email: str):
        return self.db.query(Users).filter(Users.email == email).first()


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