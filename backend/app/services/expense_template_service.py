from sqlalchemy.orm import Session
from app.models.expense import ExpenseTemplate, Expense
from app.models.category import Category, Subcategory
from app.models.account import Account
from app.models.schemas import (
    ExpenseTemplateCreate, ExpenseTemplateUpdate,
    ExpenseCreate
)
from typing import List, Optional
from datetime import datetime, date


class ExpenseTemplateService:
    def __init__(self, db: Session):
        self.db = db

    # ========== TEMPLATE METHODS ==========

    def get_templates(self, user_id: int, include_inactive: bool = False) -> List[ExpenseTemplate]:
        """Get all expense templates for a user"""
        query = self.db.query(ExpenseTemplate).filter(ExpenseTemplate.user_id == user_id)
        if not include_inactive:
            query = query.filter(ExpenseTemplate.is_active == True)
        return query.order_by(ExpenseTemplate.name).all()

    def get_templates_with_names(self, user_id: int, include_inactive: bool = False) -> List[dict]:
        """Get expense templates with category, subcategory, and account names"""
        templates = self.get_templates(user_id, include_inactive)

        result = []
        for template in templates:
            template_dict = {
                "id": template.id,
                "name": template.name,
                "amount": template.amount,
                "category_id": template.category_id,
                "subcategory_id": template.subcategory_id,
                "account_id": template.account_id,
                "user_id": template.user_id,
                "is_active": template.is_active,
                "created_at": template.created_at,
                "updated_at": template.updated_at,
                "category_name": template.category.name if template.category else None,
                "subcategory_name": template.subcategory.name if template.subcategory else None,
                "account_name": template.account.name if template.account else None
            }
            result.append(template_dict)

        return result

    def get_template_by_id(self, template_id: int, user_id: int) -> Optional[ExpenseTemplate]:
        """Get a specific expense template"""
        return self.db.query(ExpenseTemplate).filter(
            ExpenseTemplate.id == template_id,
            ExpenseTemplate.user_id == user_id
        ).first()

    def create_template(self, template: ExpenseTemplateCreate, user_id: int) -> ExpenseTemplate:
        """Create a new expense template"""
        db_template = ExpenseTemplate(**template.model_dump(), user_id=user_id)
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def update_template(self, template_id: int, user_id: int, template_update: ExpenseTemplateUpdate) -> Optional[ExpenseTemplate]:
        """Update an expense template"""
        db_template = self.get_template_by_id(template_id, user_id)
        if not db_template:
            return None

        update_data = template_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_template, field, value)

        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def delete_template(self, template_id: int, user_id: int) -> bool:
        """Delete an expense template (soft delete)"""
        db_template = self.get_template_by_id(template_id, user_id)
        if not db_template:
            return False

        db_template.is_active = False
        self.db.commit()
        return True

    # ========== EXPENSE GENERATION METHODS ==========

    def generate_monthly_expenses(self, user_id: int, year: int, month: int) -> List[Expense]:
        """
        Generate monthly expense entries from active templates for a given month.
        Creates entries with the first day of the month as the date.
        Only creates entries if they don't already exist for that month.
        """
        # Get active templates
        templates = self.get_templates(user_id, include_inactive=False)

        # Create the target date (first day of the month)
        target_date = date(year, month, 1)

        # Get existing expenses for this month to avoid duplicates
        # We'll check if there are expenses with the same category/subcategory on the first day
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1)
        else:
            month_end = date(year, month + 1, 1)

        existing_expenses = self.db.query(Expense).filter(
            Expense.user_id == user_id,
            Expense.date >= month_start,
            Expense.date < month_end
        ).all()

        # Create a set of (category_id, subcategory_id, name) for existing expenses on first day
        existing_on_first = {
            (exp.category_id, exp.subcategory_id)
            for exp in existing_expenses
            if exp.date == month_start
        }

        created_expenses = []
        for template in templates:
            # Check if an expense from this template already exists this month on the first day
            if (template.category_id, template.subcategory_id) in existing_on_first:
                continue

            # Create expense from template
            expense = Expense(
                date=target_date,
                category_id=template.category_id,
                subcategory_id=template.subcategory_id,
                amount=template.amount,
                account_id=template.account_id,
                status=True,
                user_id=user_id
            )
            self.db.add(expense)
            created_expenses.append(expense)

        if created_expenses:
            self.db.commit()
            for expense in created_expenses:
                self.db.refresh(expense)

        return created_expenses
