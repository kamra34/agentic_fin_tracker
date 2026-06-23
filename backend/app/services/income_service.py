from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models.income import IncomeTemplate, MonthlyIncome
from app.models.account import Account
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
        data = income.model_dump()
        # If no account was specified but it came from a template, inherit the template's account
        if data.get("account_id") is None and data.get("template_id"):
            template = self.get_template_by_id(data["template_id"], user_id)
            if template and template.account_id:
                data["account_id"] = template.account_id
        db_income = MonthlyIncome(**data, user_id=user_id)
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
                account_id=template.account_id,  # inherit the template's destination account
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

    # ========== ACCOUNT / OWNER ATTRIBUTION ==========

    def get_monthly_income_allocation(self, user_id: int, month: str) -> Dict:
        """Get monthly income grouped by the account it lands in (mirror of the expense allocation).

        `month` is the string 'YYYY-MM' (MonthlyIncome stores month as a string, not a date range).
        Income with no account is bucketed as 'Unassigned', exactly like NULL-account expenses.
        """
        result = self.db.query(
            MonthlyIncome.account_id,
            Account.name,
            Account.owner_name,
            func.sum(MonthlyIncome.amount).label('total_amount'),
            func.count(MonthlyIncome.id).label('income_count')
        ).outerjoin(Account, MonthlyIncome.account_id == Account.id).filter(
            MonthlyIncome.user_id == user_id,
            MonthlyIncome.month == month
        ).group_by(MonthlyIncome.account_id, Account.name, Account.owner_name).all()

        allocations = []
        total_income = 0.0
        for row in result:
            total = float(row.total_amount or 0)
            total_income += total
            if row.account_id:
                allocations.append({
                    'account_id': row.account_id,
                    'account_name': row.name or 'Unknown',
                    'owner_name': row.owner_name or 'Unknown',
                    'total_amount': total,
                    'income_count': row.income_count
                })
            else:
                allocations.append({
                    'account_id': None,
                    'account_name': 'Unassigned',
                    'owner_name': None,
                    'total_amount': total,
                    'income_count': row.income_count
                })

        return {'month': month, 'total_income': total_income, 'allocations': allocations}

    def get_monthly_owner_net(self, user_id: int, year: int, month: int, expense_service) -> Dict:
        """Per-owner and per-account NET (income into the account/owner minus expenses out of it).

        - SHARED is its own bucket (not split between people).
        - Owner names are normalized (strip/upper) for keying so 'Kamiar' and 'KAMIAR' don't split.
        - Income/expenses with no account fall under an 'Unassigned' bucket (a catch-all, NOT a person).
        - Expenses are paid-only (status == True), and income has no status, so net is
          (all income) - (paid expenses). This is intentional: it matches the Monthly page's
          existing "Expenses" and "Net" KPIs (get_monthly_summary also filters status == True),
          so the per-person nets reconcile with the global Net chip.
        """
        month_str = f"{year}-{month:02d}"
        income_alloc = self.get_monthly_income_allocation(user_id, month_str)
        expense_alloc = expense_service.get_monthly_account_allocation(user_id, year, month)

        def owner_key(name):
            return name.strip().upper() if name else 'UNASSIGNED'

        def owner_display(name):
            return name.strip() if name else 'Unassigned'

        owners = {}    # normalized owner key -> aggregate
        accounts = {}  # account_id (or 'unassigned') -> aggregate

        def bump_owner(name, field, amount):
            k = owner_key(name)
            if k not in owners:
                owners[k] = {'owner_name': owner_display(name), 'income_total': 0.0, 'expense_total': 0.0}
            owners[k][field] += amount

        def bump_account(account_id, account_name, owner_name, field, amount):
            k = account_id if account_id is not None else 'unassigned'
            if k not in accounts:
                accounts[k] = {
                    'account_id': account_id,
                    'account_name': account_name or 'Unassigned',
                    'owner_name': owner_display(owner_name) if owner_name else None,
                    'income_total': 0.0,
                    'expense_total': 0.0,
                }
            accounts[k][field] += amount

        for a in income_alloc['allocations']:
            bump_owner(a['owner_name'], 'income_total', a['total_amount'])
            bump_account(a['account_id'], a['account_name'], a['owner_name'], 'income_total', a['total_amount'])
        for a in expense_alloc['allocations']:
            bump_owner(a['owner_name'], 'expense_total', a['total_amount'])
            bump_account(a['account_id'], a['account_name'], a['owner_name'], 'expense_total', a['total_amount'])

        owner_list = []
        for v in owners.values():
            v['net'] = v['income_total'] - v['expense_total']
            owner_list.append(v)
        owner_list.sort(key=lambda x: x['owner_name'] or 'zzz')

        account_list = []
        for v in accounts.values():
            v['net'] = v['income_total'] - v['expense_total']
            account_list.append(v)
        account_list.sort(key=lambda x: (x['owner_name'] or 'zzz', x['account_name'] or ''))

        total_income = income_alloc['total_income']
        total_expenses = expense_alloc['total_expenses']
        return {
            'year': year,
            'month': month,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net': total_income - total_expenses,
            'owners': owner_list,
            'accounts': account_list,
        }
