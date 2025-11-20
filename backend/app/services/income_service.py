from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.income import IncomeTemplate, MonthlyIncome
from app.models.schemas import (
    IncomeTemplateCreate, IncomeTemplateUpdate,
    MonthlyIncomeCreate, MonthlyIncomeUpdate
)
from typing import List, Optional, Dict
from datetime import datetime


class IncomeService:
    def __init__(self, db: Session):
        self.db = db

    # ========== TEMPLATE METHODS ==========

    def get_templates(self, user_id: int, include_inactive: bool = False) -> List[IncomeTemplate]:
        """Get all income templates for a user"""
        query = self.db.query(IncomeTemplate).filter(IncomeTemplate.user_id == user_id)
        if not include_inactive:
            query = query.filter(IncomeTemplate.is_active == True)
        return query.order_by(IncomeTemplate.source_name).all()

    def get_template_by_id(self, template_id: int, user_id: int) -> Optional[IncomeTemplate]:
        """Get a specific income template"""
        return self.db.query(IncomeTemplate).filter(
            IncomeTemplate.id == template_id,
            IncomeTemplate.user_id == user_id
        ).first()

    def create_template(self, template: IncomeTemplateCreate, user_id: int) -> IncomeTemplate:
        """Create a new income template"""
        db_template = IncomeTemplate(**template.model_dump(), user_id=user_id)
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        return db_template

    def update_template(self, template_id: int, user_id: int, template_update: IncomeTemplateUpdate) -> Optional[IncomeTemplate]:
        """Update an income template"""
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
        """Delete an income template (soft delete)"""
        db_template = self.get_template_by_id(template_id, user_id)
        if not db_template:
            return False

        db_template.is_active = False
        self.db.commit()
        return True

    # ========== MONTHLY INCOME METHODS ==========

    def get_monthly_incomes(self, user_id: int, month: Optional[str] = None) -> List[MonthlyIncome]:
        """Get monthly income entries, optionally filtered by month"""
        query = self.db.query(MonthlyIncome).filter(MonthlyIncome.user_id == user_id)

        if month:
            query = query.filter(MonthlyIncome.month == month)

        return query.order_by(MonthlyIncome.month.desc(), MonthlyIncome.source_name).all()

    def get_monthly_income_by_id(self, income_id: int, user_id: int) -> Optional[MonthlyIncome]:
        """Get a specific monthly income entry"""
        return self.db.query(MonthlyIncome).filter(
            MonthlyIncome.id == income_id,
            MonthlyIncome.user_id == user_id
        ).first()

    def create_monthly_income(self, income: MonthlyIncomeCreate, user_id: int) -> MonthlyIncome:
        """Create a new monthly income entry"""
        db_income = MonthlyIncome(**income.model_dump(), user_id=user_id)
        self.db.add(db_income)
        self.db.commit()
        self.db.refresh(db_income)
        return db_income

    def update_monthly_income(self, income_id: int, user_id: int, income_update: MonthlyIncomeUpdate) -> Optional[MonthlyIncome]:
        """Update a monthly income entry"""
        db_income = self.get_monthly_income_by_id(income_id, user_id)
        if not db_income:
            return None

        update_data = income_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_income, field, value)

        self.db.commit()
        self.db.refresh(db_income)
        return db_income

    def delete_monthly_income(self, income_id: int, user_id: int) -> bool:
        """Delete a monthly income entry (hard delete since it's monthly data)"""
        db_income = self.get_monthly_income_by_id(income_id, user_id)
        if not db_income:
            return False

        self.db.delete(db_income)
        self.db.commit()
        return True

    # ========== UTILITY METHODS ==========

    def generate_monthly_incomes(self, user_id: int, month: str) -> List[MonthlyIncome]:
        """
        Generate monthly income entries from active templates for a given month.
        Only creates entries if they don't already exist for that month.
        """
        # Check if incomes already exist for this month
        existing = self.get_monthly_incomes(user_id, month)
        template_ids_with_entries = {inc.template_id for inc in existing if inc.template_id}

        # Get active templates
        templates = self.get_templates(user_id, include_inactive=False)

        created_incomes = []
        for template in templates:
            # Skip if already has an entry for this month
            if template.id in template_ids_with_entries:
                continue

            # Create monthly income from template
            monthly_income = MonthlyIncome(
                month=month,
                template_id=template.id,
                source_name=template.source_name,
                amount=template.current_amount,
                is_one_time=False,
                user_id=user_id
            )
            self.db.add(monthly_income)
            created_incomes.append(monthly_income)

        if created_incomes:
            self.db.commit()
            for income in created_incomes:
                self.db.refresh(income)

        return created_incomes

    def get_monthly_total(self, user_id: int, month: str) -> float:
        """Get total income for a specific month"""
        result = self.db.query(func.sum(MonthlyIncome.amount)).filter(
            MonthlyIncome.user_id == user_id,
            MonthlyIncome.month == month
        ).scalar()

        return float(result or 0)

    def get_income_by_source(self, user_id: int, month: Optional[str] = None) -> List[Dict]:
        """Get income grouped by source"""
        query = self.db.query(
            MonthlyIncome.source_name,
            func.sum(MonthlyIncome.amount).label('total'),
            func.count(MonthlyIncome.id).label('count')
        ).filter(MonthlyIncome.user_id == user_id)

        if month:
            query = query.filter(MonthlyIncome.month == month)

        query = query.group_by(MonthlyIncome.source_name).order_by(func.sum(MonthlyIncome.amount).desc())

        results = query.all()
        return [
            {
                'source': r.source_name,
                'total': float(r.total),
                'count': r.count
            }
            for r in results
        ]
