from sqlalchemy.orm import Session
from app.models.category import Category
from app.models.schemas import CategoryCreate
from typing import List, Optional

class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    def create_category(self, category: CategoryCreate) -> Category:
        db_category = Category(**category.model_dump())
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def get_categories(self) -> List[Category]:
        return self.db.query(Category).all()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        return self.db.query(Category).filter(Category.id == category_id).first()

    def delete_category(self, category_id: int) -> bool:
        db_category = self.get_category_by_id(category_id)
        if not db_category:
            return False

        self.db.delete(db_category)
        self.db.commit()
        return True
