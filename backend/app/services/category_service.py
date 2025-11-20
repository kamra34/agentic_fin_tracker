from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.category import Category, Subcategory
from app.models.expense import Expense
from app.models.schemas import CategoryCreate, CategoryUpdate, SubcategoryCreate, SubcategoryUpdate
from typing import List, Optional, Dict


class CategoryService:
    def __init__(self, db: Session):
        self.db = db

    # Category methods
    def get_categories(self, user_id: int, include_inactive: bool = False, category_type: Optional[str] = None) -> List[Category]:
        """Get all categories for a user, optionally filtered by type"""
        query = self.db.query(Category).filter(Category.user_id == user_id)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        if category_type:
            query = query.filter(Category.category_type == category_type)
        return query.order_by(Category.name).all()

    def get_category_by_id(self, category_id: int, user_id: int) -> Optional[Category]:
        """Get a specific category"""
        return self.db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == user_id
        ).first()

    def create_category(self, category: CategoryCreate, user_id: int) -> Category:
        """Create a new category"""
        db_category = Category(**category.model_dump(), user_id=user_id)
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def update_category(self, category_id: int, user_id: int, category_update: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        db_category = self.get_category_by_id(category_id, user_id)
        if not db_category:
            return None

        update_data = category_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)

        self.db.commit()
        self.db.refresh(db_category)
        return db_category

    def delete_category(self, category_id: int, user_id: int) -> bool:
        """Delete a category (sets inactive instead)"""
        db_category = self.get_category_by_id(category_id, user_id)
        if not db_category:
            return False

        db_category.is_active = False
        self.db.commit()
        return True

    def merge_categories(self, source_id: int, target_id: int, user_id: int) -> bool:
        """Merge source category into target category"""
        source = self.get_category_by_id(source_id, user_id)
        target = self.get_category_by_id(target_id, user_id)

        if not source or not target:
            return False

        # Update all expenses from source to target
        self.db.query(Expense).filter(
            Expense.category_id == source_id,
            Expense.user_id == user_id
        ).update({"category_id": target_id, "category": target.name})

        # Delete source category
        self.db.delete(source)
        self.db.commit()
        return True

    def get_categories_with_stats(self, user_id: int) -> List[Dict]:
        """Get categories with expense counts and totals"""
        categories = self.get_categories(user_id)
        result = []

        for category in categories:
            stats = self.db.query(
                func.count(Expense.id).label('count'),
                func.sum(Expense.amount).label('total')
            ).filter(
                Expense.category_id == category.id,
                Expense.user_id == user_id,
                Expense.status == True
            ).first()

            # Get subcategories with their statistics (only active ones)
            subcategories_with_stats = []
            for sub in category.subcategories:
                # Skip inactive subcategories
                if not sub.is_active:
                    continue

                sub_stats = self.db.query(
                    func.count(Expense.id).label('count'),
                    func.sum(Expense.amount).label('total')
                ).filter(
                    Expense.subcategory_id == sub.id,
                    Expense.user_id == user_id,
                    Expense.status == True
                ).first()

                subcategories_with_stats.append({
                    'id': sub.id,
                    'name': sub.name,
                    'is_active': sub.is_active,
                    'expense_count': sub_stats.count or 0,
                    'total_amount': float(sub_stats.total or 0)
                })

            result.append({
                'id': category.id,
                'name': category.name,
                'category_type': category.category_type,
                'is_active': category.is_active,
                'expense_count': stats.count or 0,
                'total_amount': float(stats.total or 0),
                'subcategories': subcategories_with_stats
            })

        return result

    # Subcategory methods
    def get_subcategories(self, category_id: int, user_id: int) -> List[Subcategory]:
        """Get all subcategories for a category"""
        # Verify category belongs to user
        category = self.get_category_by_id(category_id, user_id)
        if not category:
            return []

        return self.db.query(Subcategory).filter(
            Subcategory.category_id == category_id,
            Subcategory.is_active == True
        ).order_by(Subcategory.name).all()

    def create_subcategory(self, subcategory: SubcategoryCreate, user_id: int) -> Optional[Subcategory]:
        """Create a new subcategory"""
        # Verify category belongs to user
        category = self.get_category_by_id(subcategory.category_id, user_id)
        if not category:
            return None

        db_subcategory = Subcategory(**subcategory.model_dump())
        self.db.add(db_subcategory)
        self.db.commit()
        self.db.refresh(db_subcategory)
        return db_subcategory

    def update_subcategory(self, subcategory_id: int, user_id: int, subcategory_update: SubcategoryUpdate) -> Optional[Subcategory]:
        """Update a subcategory"""
        db_subcategory = self.db.query(Subcategory).filter(
            Subcategory.id == subcategory_id
        ).first()

        if not db_subcategory:
            return None

        # Verify user owns the parent category
        category = self.get_category_by_id(db_subcategory.category_id, user_id)
        if not category:
            return None

        update_data = subcategory_update.model_dump(exclude_unset=True)

        # If updating name, check for duplicates (excluding current subcategory and inactive ones)
        if 'name' in update_data and update_data['name'] != db_subcategory.name:
            existing = self.db.query(Subcategory).filter(
                Subcategory.category_id == db_subcategory.category_id,
                Subcategory.name == update_data['name'],
                Subcategory.id != subcategory_id,
                Subcategory.is_active == True
            ).first()
            if existing:
                return None  # Name already exists in this category

        for field, value in update_data.items():
            setattr(db_subcategory, field, value)

        self.db.commit()
        self.db.refresh(db_subcategory)
        return db_subcategory

    def delete_subcategory(self, subcategory_id: int, user_id: int) -> bool:
        """Delete a subcategory (soft delete by marking inactive and renaming to avoid unique constraint)"""
        db_subcategory = self.db.query(Subcategory).filter(
            Subcategory.id == subcategory_id
        ).first()

        if not db_subcategory:
            return False

        # Verify user owns the parent category
        category = self.get_category_by_id(db_subcategory.category_id, user_id)
        if not category:
            return False

        # Mark as inactive and rename to avoid unique constraint conflicts
        # Format: "_deleted_<id>_<original_name>"
        db_subcategory.is_active = False
        db_subcategory.name = f"_deleted_{db_subcategory.id}_{db_subcategory.name}"[:100]
        self.db.commit()
        return True
