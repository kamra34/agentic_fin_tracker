from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.expense import Expense
from app.models.schemas import DashboardStats


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_stats(self, user_id: int) -> DashboardStats:
        """Get dashboard statistics for a user"""
        # Calculate total expenses
        total_expenses = self.db.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.status == True
        ).scalar() or 0.0

        # Count total expenses
        expense_count = self.db.query(func.count(Expense.id)).filter(
            Expense.user_id == user_id
        ).scalar() or 0

        # Count active expenses
        active_expense_count = self.db.query(func.count(Expense.id)).filter(
            Expense.user_id == user_id,
            Expense.status == True
        ).scalar() or 0

        # Get categories summary
        categories_result = self.db.query(
            Expense.category,
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == user_id,
            Expense.status == True
        ).group_by(Expense.category).all()

        categories_summary = {
            row.category: {
                'total_amount': float(row.total_amount or 0),
                'count': row.count
            }
            for row in categories_result
        }

        return DashboardStats(
            total_expenses=total_expenses,
            expense_count=expense_count,
            active_expense_count=active_expense_count,
            categories_summary=categories_summary
        )
