from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from app.models.user import User
from app.models.expense import Expense, ExpenseTemplate
from app.models.category import Category, Subcategory
from app.models.account import Account
from app.models.income import IncomeTemplate, MonthlyIncome
from app.models.savings import SavingsAccount, SavingsTransaction


class ChatDataService:
    """
    Service for retrieving READ-ONLY data for AI agents.
    NO CRUD OPERATIONS - only data retrieval and analysis.
    """

    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_database_schema(self) -> Dict[str, Any]:
        """Returns complete database schema information"""
        return {
            "tables": {
                "users": {
                    "description": "User profiles with financial goals",
                    "columns": [
                        "id", "email", "full_name", "currency", "timezone", "is_active",
                        "household_members", "num_vehicles", "housing_type",
                        "house_size_sqm", "monthly_income_goal", "monthly_savings_goal",
                        "created_at", "updated_at"
                    ]
                },
                "expenses": {
                    "description": "Daily expense records",
                    "columns": [
                        "id", "user_id", "date", "category_id", "subcategory_id",
                        "amount", "status", "account_id"
                    ],
                    "relationships": ["user", "category", "subcategory", "account"]
                },
                "categories": {
                    "description": "Expense/Income categories",
                    "columns": [
                        "id", "user_id", "name", "category_type", "is_active"
                    ],
                    "relationships": ["subcategories", "expenses"]
                },
                "subcategories": {
                    "description": "Subcategories under main categories",
                    "columns": [
                        "id", "category_id", "name", "is_active"
                    ]
                },
                "accounts": {
                    "description": "Payment accounts (bank accounts, credit cards)",
                    "columns": [
                        "id", "user_id", "name", "owner_name"
                    ],
                    "relationships": ["expenses"]
                },
                "savings_accounts": {
                    "description": "Investment and savings accounts",
                    "columns": [
                        "id", "user_id", "name", "account_type", "description",
                        "is_active", "created_at", "updated_at"
                    ],
                    "relationships": ["transactions"]
                },
                "savings_transactions": {
                    "description": "Deposits, withdrawals, and value updates",
                    "columns": [
                        "id", "account_id", "transaction_type", "amount",
                        "transaction_date", "notes", "created_at"
                    ],
                    "types": ["deposit", "withdrawal", "value_update"]
                },
                "income_templates": {
                    "description": "Recurring income sources",
                    "columns": [
                        "id", "user_id", "source_name", "current_amount",
                        "is_active", "created_at", "updated_at"
                    ]
                },
                "monthly_incomes": {
                    "description": "Actual monthly income entries",
                    "columns": [
                        "id", "user_id", "month", "template_id", "source_name",
                        "amount", "is_one_time", "description"
                    ]
                },
                "expense_templates": {
                    "description": "Recurring expense templates",
                    "columns": [
                        "id", "user_id", "name", "amount", "category_id",
                        "subcategory_id", "account_id", "is_active",
                        "created_at", "updated_at"
                    ]
                }
            }
        }

    def get_user_profile(self) -> Dict[str, Any]:
        """Get current user's profile and financial goals - THIS IS CRITICAL CONTEXT"""
        user = self.db.query(User).filter(User.id == self.user_id).first()
        if not user:
            return {}

        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "currency": user.currency,
            "timezone": user.timezone or "UTC",
            "household_info": {
                "household_members": user.household_members or "Not specified",
                "num_vehicles": user.num_vehicles or "Not specified",
                "housing_type": user.housing_type or "Not specified",
                "house_size_sqm": user.house_size_sqm or "Not specified"
            },
            "financial_goals": {
                "monthly_income_goal": user.monthly_income_goal or "Not set",
                "monthly_savings_goal": user.monthly_savings_goal or "Not set"
            },
            "account_created": user.created_at.isoformat() if user.created_at else None,
            "note": f"Always use {user.currency} when displaying amounts. User's name is {user.full_name}. User's timezone is {user.timezone or 'UTC'}."
        }

    def get_spending_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """Get spending summary for a date range"""
        query = self.db.query(Expense).filter(Expense.user_id == self.user_id)

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        expenses = query.all()

        total_spent = sum(exp.amount or 0 for exp in expenses)
        active_expenses = [exp for exp in expenses if exp.status]
        total_active_spent = sum(exp.amount or 0 for exp in active_expenses)

        return {
            "total_expenses": len(expenses),
            "total_amount": round(total_spent, 2),
            "active_expenses": len(active_expenses),
            "active_amount": round(total_active_spent, 2),
            "date_range": {
                "start": start_date,
                "end": end_date
            }
        }

    def get_category_breakdown(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get spending breakdown by category"""
        query = self.db.query(
            Category.name,
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count")
        ).join(
            Expense, Expense.category_id == Category.id
        ).filter(
            Expense.user_id == self.user_id,
            Expense.status == True
        )

        if start_date:
            query = query.filter(Expense.date >= start_date)
        if end_date:
            query = query.filter(Expense.date <= end_date)

        results = query.group_by(Category.name).all()

        return [
            {
                "category": row.name,
                "total_amount": round(float(row.total_amount or 0), 2),
                "count": row.count
            }
            for row in results
        ]

    def get_subcategory_breakdown(self, category_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get spending breakdown by subcategory"""
        query = self.db.query(
            Category.name.label("category_name"),
            Subcategory.name.label("subcategory_name"),
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count")
        ).join(
            Expense, Expense.subcategory_id == Subcategory.id
        ).join(
            Category, Expense.category_id == Category.id
        ).filter(
            Expense.user_id == self.user_id,
            Expense.status == True
        )

        if category_name:
            query = query.filter(Category.name == category_name)

        results = query.group_by(Category.name, Subcategory.name).all()

        return [
            {
                "category": row.category_name,
                "subcategory": row.subcategory_name,
                "total_amount": round(float(row.total_amount or 0), 2),
                "count": row.count
            }
            for row in results
        ]

    def get_account_summary(self) -> List[Dict[str, Any]]:
        """Get spending summary by payment account"""
        results = self.db.query(
            Account.name,
            Account.owner_name,
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count")
        ).join(
            Expense, Expense.account_id == Account.id
        ).filter(
            Expense.user_id == self.user_id,
            Expense.status == True
        ).group_by(Account.name, Account.owner_name).all()

        return [
            {
                "account_name": row.name,
                "owner_name": row.owner_name,
                "total_amount": round(float(row.total_amount or 0), 2),
                "expense_count": row.count
            }
            for row in results
        ]

    def get_monthly_trends(self, months: int = 6) -> List[Dict[str, Any]]:
        """Get monthly spending trends"""
        results = self.db.query(
            extract('year', Expense.date).label('year'),
            extract('month', Expense.date).label('month'),
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('count')
        ).filter(
            Expense.user_id == self.user_id,
            Expense.status == True
        ).group_by('year', 'month').order_by('year', 'month').limit(months).all()

        return [
            {
                "year": int(row.year),
                "month": int(row.month),
                "total_amount": round(float(row.total_amount or 0), 2),
                "expense_count": row.count
            }
            for row in results
        ]

    def get_savings_summary(self) -> Dict[str, Any]:
        """Get complete savings and investment summary"""
        savings_accounts = self.db.query(SavingsAccount).filter(
            SavingsAccount.user_id == self.user_id,
            SavingsAccount.is_active == 1
        ).all()

        total_deposits = 0
        total_withdrawals = 0
        accounts_data = []

        for account in savings_accounts:
            deposits = self.db.query(func.sum(SavingsTransaction.amount)).filter(
                SavingsTransaction.account_id == account.id,
                SavingsTransaction.transaction_type == 'deposit'
            ).scalar() or 0

            withdrawals = self.db.query(func.sum(SavingsTransaction.amount)).filter(
                SavingsTransaction.account_id == account.id,
                SavingsTransaction.transaction_type == 'withdrawal'
            ).scalar() or 0

            latest_value = self.db.query(SavingsTransaction.amount).filter(
                SavingsTransaction.account_id == account.id,
                SavingsTransaction.transaction_type == 'value_update'
            ).order_by(SavingsTransaction.transaction_date.desc()).first()

            current_value = latest_value[0] if latest_value else deposits - withdrawals
            net_deposits = deposits - withdrawals
            profit_loss = current_value - net_deposits

            total_deposits += deposits
            total_withdrawals += withdrawals

            accounts_data.append({
                "account_name": account.name,
                "account_type": account.account_type,
                "total_deposits": round(float(deposits), 2),
                "total_withdrawals": round(float(withdrawals), 2),
                "net_deposits": round(float(net_deposits), 2),
                "current_value": round(float(current_value), 2),
                "profit_loss": round(float(profit_loss), 2),
                "profit_loss_percentage": round((profit_loss / net_deposits * 100) if net_deposits > 0 else 0, 2)
            })

        return {
            "total_accounts": len(savings_accounts),
            "total_deposits": round(float(total_deposits), 2),
            "total_withdrawals": round(float(total_withdrawals), 2),
            "accounts": accounts_data
        }

    def get_current_income_sources(self) -> Dict[str, Any]:
        """Get CURRENT/LATEST recurring income sources (from templates) - NOT historical totals"""
        templates = self.db.query(IncomeTemplate).filter(
            IncomeTemplate.user_id == self.user_id,
            IncomeTemplate.is_active == True
        ).all()

        sources = []
        total_current = 0
        for template in templates:
            sources.append({
                "source_name": template.source_name,
                "current_amount": round(template.current_amount, 2)
            })
            total_current += template.current_amount

        return {
            "total_current_monthly_income": round(total_current, 2),
            "income_sources": sources,
            "note": "These are CURRENT recurring income amounts, not historical totals"
        }

    def get_income_summary(self, month: Optional[str] = None) -> Dict[str, Any]:
        """Get income summary for a specific month or all time - WARNING: without month parameter, sums ALL historical income"""
        query = self.db.query(MonthlyIncome).filter(MonthlyIncome.user_id == self.user_id)

        if month:
            query = query.filter(MonthlyIncome.month == month)
        else:
            # If no month specified, only get current month to avoid confusion
            from datetime import datetime
            month = datetime.now().strftime("%Y-%m")
            query = query.filter(MonthlyIncome.month == month)

        incomes = query.all()

        total_income = sum(inc.amount for inc in incomes)
        recurring_income = sum(inc.amount for inc in incomes if not inc.is_one_time)
        one_time_income = sum(inc.amount for inc in incomes if inc.is_one_time)

        income_sources = {}
        for inc in incomes:
            if inc.source_name not in income_sources:
                income_sources[inc.source_name] = 0
            income_sources[inc.source_name] += inc.amount

        return {
            "total_income": round(total_income, 2),
            "recurring_income": round(recurring_income, 2),
            "one_time_income": round(one_time_income, 2),
            "income_count": len(incomes),
            "sources": [
                {"source": source, "amount": round(amount, 2)}
                for source, amount in income_sources.items()
            ],
            "month": month,
            "note": f"This is income for month: {month}. For CURRENT income sources, use get_current_income_sources()"
        }

    def get_expense_templates(self) -> List[Dict[str, Any]]:
        """Get all recurring expense templates"""
        templates = self.db.query(ExpenseTemplate).filter(
            ExpenseTemplate.user_id == self.user_id,
            ExpenseTemplate.is_active == True
        ).all()

        result = []
        for template in templates:
            category = self.db.query(Category).filter(Category.id == template.category_id).first()
            subcategory = None
            if template.subcategory_id:
                subcategory = self.db.query(Subcategory).filter(Subcategory.id == template.subcategory_id).first()

            result.append({
                "name": template.name,
                "amount": round(template.amount, 2),
                "category": category.name if category else None,
                "subcategory": subcategory.name if subcategory else None
            })

        return result

    def get_financial_health_metrics(self) -> Dict[str, Any]:
        """Calculate overall financial health metrics"""
        user = self.db.query(User).filter(User.id == self.user_id).first()

        current_month = datetime.now().strftime("%Y-%m")
        month_income = self.get_income_summary(current_month)["total_income"]
        month_expenses = self.get_spending_summary(
            start_date=f"{current_month}-01",
            end_date=datetime.now().strftime("%Y-%m-%d")
        )["active_amount"]

        savings_data = self.get_savings_summary()
        total_savings_value = sum(acc["current_value"] for acc in savings_data["accounts"])

        monthly_savings_rate = ((month_income - month_expenses) / month_income * 100) if month_income > 0 else 0

        return {
            "monthly_income": round(month_income, 2),
            "monthly_expenses": round(month_expenses, 2),
            "monthly_savings": round(month_income - month_expenses, 2),
            "savings_rate_percentage": round(monthly_savings_rate, 2),
            "total_savings_value": round(total_savings_value, 2),
            "income_goal": user.monthly_income_goal if user else None,
            "savings_goal": user.monthly_savings_goal if user else None,
            "currency": user.currency if user else "SEK"
        }
