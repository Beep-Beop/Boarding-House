from sqlalchemy.orm import Session
from src.models import Photo, EntityTypeEnum

class PhotoCRUD:
    def __init__(self, db_session: Session):
        self.db = db_session

    def create(self, entity_type: EntityTypeEnum, entity_id: int, photo_url: str, is_primary: bool = False, sort_order: int = 0) -> Photo:
        db_photo = Photo(
            entity_type=entity_type,
            entity_id=entity_id,
            photo_url=photo_url,
            is_primary=is_primary,
            sort_order=sort_order
        )
        self.db.add(db_photo)
        self.db.commit()
        self.db.refresh(db_photo)
        return db_photo

    def get(self, photo_id: int) -> Photo:
        return self.db.query(Photo).filter(Photo.photo_id == photo_id).first()

    def delete(self, photo_id: int) -> bool:
        photo = self.get(photo_id)
        if photo:
            self.db.delete(photo)
            self.db.commit()
            return True
        return False