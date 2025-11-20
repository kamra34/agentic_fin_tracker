from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.expense import Expense
from app.models.category import Category, Subcategory
from app.models.schemas import ExpenseCreate, ExpenseUpdate
from typing import List, Optional, Dict
from datetime import date, datetime
from calendar import monthrange


class ExpenseService:
    def __init__(self, db: Session):
        self.db = db

    def _enrich_expense_with_names(self, expense: Expense) -> Expense:
        """Add category_name and subcategory_name attributes to expense object"""
        if expense.category_id:
            category = self.db.query(Category).filter(Category.id == expense.category_id).first()
            expense.category_name = category.name if category else None
        else:
            expense.category_name = None

        if expense.subcategory_id:
            subcategory = self.db.query(Subcategory).filter(Subcategory.id == expense.subcategory_id).first()
            expense.subcategory_name = subcategory.name if subcategory else None
        else:
            expense.subcategory_name = None

        return expense

    def create_expense(self, expense: ExpenseCreate, user_id: int) -> Expense:
        """Create a new expense"""
        db_expense = Expense(**expense.model_dump(), user_id=user_id)
        self.db.add(db_expense)
        self.db.commit()
        self.db.refresh(db_expense)
        return self._enrich_expense_with_names(db_expense)

    def get_expenses(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[bool] = None
    ) -> List[Expense]:
        """Get expenses with optional filters"""
        query = self.db.query(Expense).filter(Expense.user_id == user_id)

        if category:
            query = query.filter(Expense.category == category)

        if start_date:
            query = query.filter(Expense.date >= start_date)

        if end_date:
            query = query.filter(Expense.date <= end_date)

        if status is not None:
            query = query.filter(Expense.status == status)

        expenses = query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()
        return [self._enrich_expense_with_names(exp) for exp in expenses]

    def get_expense_by_id(self, expense_id: int, user_id: int) -> Optional[Expense]:
        """Get a specific expense by ID for a user"""
        expense = self.db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == user_id
        ).first()
        return self._enrich_expense_with_names(expense) if expense else None

    def update_expense(
        self,
        expense_id: int,
        user_id: int,
        expense_update: ExpenseUpdate
    ) -> Optional[Expense]:
        """Update an expense"""
        db_expense = self.db.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == user_id
        ).first()
        if not db_expense:
            return None

        update_data = expense_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_expense, field, value)

        self.db.commit()
        self.db.refresh(db_expense)
        return self._enrich_expense_with_names(db_expense)

    def delete_expense(self, expense_id: int, user_id: int) -> bool:
        """Delete an expense"""
        db_expense = self.get_expense_by_id(expense_id, user_id)
        if not db_expense:
            return False

        self.db.delete(db_expense)
        self.db.commit()
        return True

    def get_categories(self, user_id: int) -> List[str]:
        """Get all unique categories for a user"""
        result = self.db.query(Expense.category).filter(
            Expense.user_id == user_id
        ).distinct().all()
        return [row[0] for row in result]

    def get_subcategories(self, user_id: int, category: Optional[str] = None) -> List[str]:
        """Get all unique subcategories for a user, optionally filtered by category"""
        query = self.db.query(Expense.subcategory).filter(
            Expense.user_id == user_id,
            Expense.subcategory.isnot(None)
        )

        if category:
            query = query.filter(Expense.category == category)

        result = query.distinct().all()
        return [row[0] for row in result if row[0]]

    def get_expenses_summary_by_category(self, user_id: int) -> dict:
        """Get expenses summary grouped by category"""
        result = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == user_id,
            Expense.status == True
        ).group_by(Expense.category).all()

        return {
            row.category: {
                'total_amount': float(row.total_amount or 0),
                'count': row.count
            }
            for row in result
        }

    def get_monthly_expenses(self, user_id: int, year: int, month: int) -> List[Expense]:
        """Get all expenses for a specific month"""
        # Get first and last day of month
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        expenses = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        ).order_by(Expense.date.desc()).all()
        return [self._enrich_expense_with_names(exp) for exp in expenses]

    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict:
        """Get summary statistics for a specific month"""
        _, last_day = monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        # Get total and count
        result = self.db.query(
            func.sum(Expense.amount).label('total'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            Expense.status == True
        ).first()

        # Get category breakdown
        category_result = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label('total_amount')
        ).filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
            Expense.status == True
        ).group_by(Expense.category).all()

        return {
            'total': float(result.total or 0),
            'count': result.count or 0,
            'by_category': {
                row.category: float(row.total_amount or 0)
                for row in category_result
            }
        }

    def get_available_months(self, user_id: int) -> List[Dict[str, int]]:
        """Get list of year/month combinations that have expenses"""
        result = self.db.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month')
        ).filter(
            Expense.user_id == user_id
        ).distinct().order_by(
            extract('year', Expense.date).desc(),
            extract('month', Expense.date).desc()
        ).all()

        return [
            {'year': int(row.year), 'month': int(row.month)}
            for row in result
        ]

    def get_categories_with_subcategories(self, user_id: int) -> List[Dict]:
        """Get all categories with their subcategories and expense counts"""
        # Get all unique category-subcategory combinations with counts
        result = self.db.query(
            Expense.category,
            Expense.subcategory,
            func.count(Expense.id).label('count'),
            func.sum(Expense.amount).label('total_amount')
        ).filter(
            Expense.user_id == user_id
        ).group_by(
            Expense.category,
            Expense.subcategory
        ).order_by(
            Expense.category,
            Expense.subcategory
        ).all()

        # Group by category
        categories_dict = {}
        for row in result:
            category = row.category
            subcategory = row.subcategory
            count = row.count
            total = float(row.total_amount or 0)

            if category not in categories_dict:
                categories_dict[category] = {
                    'name': category,
                    'total_count': 0,
                    'total_amount': 0,
                    'subcategories': []
                }

            categories_dict[category]['total_count'] += count
            categories_dict[category]['total_amount'] += total

            if subcategory:
                categories_dict[category]['subcategories'].append({
                    'name': subcategory,
                    'count': count,
                    'total_amount': total
                })

        return list(categories_dict.values())
