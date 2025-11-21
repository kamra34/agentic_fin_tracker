from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.savings import SavingsAccount, SavingsTransaction
from app.models.schemas import (
    SavingsAccountCreate,
    SavingsAccountUpdate,
    SavingsTransactionCreate,
    SavingsTransactionUpdate
)
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime


class SavingsService:
    """Service for managing savings accounts and transactions"""

    @staticmethod
    def get_accounts(db: Session, user_id: int, include_inactive: bool = False) -> List[SavingsAccount]:
        """Get all savings accounts for a user"""
        query = db.query(SavingsAccount).filter(SavingsAccount.user_id == user_id)
        if not include_inactive:
            query = query.filter(SavingsAccount.is_active == 1)
        return query.order_by(SavingsAccount.created_at.desc()).all()

    @staticmethod
    def get_account_by_id(db: Session, account_id: int, user_id: int) -> Optional[SavingsAccount]:
        """Get a specific savings account"""
        return db.query(SavingsAccount).filter(
            SavingsAccount.id == account_id,
            SavingsAccount.user_id == user_id
        ).first()

    @staticmethod
    def create_account(db: Session, account: SavingsAccountCreate, user_id: int) -> SavingsAccount:
        """Create a new savings account"""
        db_account = SavingsAccount(
            user_id=user_id,
            **account.dict()
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account

    @staticmethod
    def update_account(
        db: Session,
        account_id: int,
        account_update: SavingsAccountUpdate,
        user_id: int
    ) -> Optional[SavingsAccount]:
        """Update a savings account"""
        db_account = SavingsService.get_account_by_id(db, account_id, user_id)
        if not db_account:
            return None

        update_data = account_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_account, field, value)

        db_account.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_account)
        return db_account

    @staticmethod
    def delete_account(db: Session, account_id: int, user_id: int) -> bool:
        """Delete a savings account (also deletes all transactions via cascade)"""
        db_account = SavingsService.get_account_by_id(db, account_id, user_id)
        if not db_account:
            return False

        db.delete(db_account)
        db.commit()
        return True

    @staticmethod
    def get_transactions(
        db: Session,
        account_id: int,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[SavingsTransaction]:
        """Get all transactions for a savings account"""
        # Verify account belongs to user
        account = SavingsService.get_account_by_id(db, account_id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Savings account not found")

        query = db.query(SavingsTransaction).filter(
            SavingsTransaction.account_id == account_id
        ).order_by(SavingsTransaction.transaction_date.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def create_transaction(
        db: Session,
        transaction: SavingsTransactionCreate,
        user_id: int
    ) -> SavingsTransaction:
        """Create a new savings transaction"""
        # Verify account belongs to user
        account = SavingsService.get_account_by_id(db, transaction.account_id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Savings account not found")

        # Validate transaction type
        valid_types = ['deposit', 'withdrawal', 'value_update']
        if transaction.transaction_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid transaction type. Must be one of: {', '.join(valid_types)}"
            )

        # Create the main transaction
        db_transaction = SavingsTransaction(**transaction.dict())
        db.add(db_transaction)
        db.commit()
        db.refresh(db_transaction)

        # Auto-update portfolio value for deposits and withdrawals
        if transaction.transaction_type in ['deposit', 'withdrawal']:
            # Get current value (latest value_update before or at this transaction date)
            latest_value = db.query(SavingsTransaction).filter(
                SavingsTransaction.account_id == transaction.account_id,
                SavingsTransaction.transaction_type == 'value_update',
                SavingsTransaction.transaction_date <= transaction.transaction_date
            ).order_by(SavingsTransaction.transaction_date.desc()).first()

            current_value = latest_value.amount if latest_value else 0

            # Calculate new value
            if transaction.transaction_type == 'deposit':
                new_value = current_value + transaction.amount
            else:  # withdrawal
                new_value = current_value - transaction.amount

            # Create automatic value_update transaction at the same date/time
            auto_value_update = SavingsTransaction(
                account_id=transaction.account_id,
                transaction_type='value_update',
                amount=new_value,
                transaction_date=transaction.transaction_date,
                notes=f"Auto-updated after {transaction.transaction_type}"
            )
            db.add(auto_value_update)
            db.commit()

        return db_transaction

    @staticmethod
    def update_transaction(
        db: Session,
        transaction_id: int,
        transaction_update: SavingsTransactionUpdate,
        user_id: int
    ) -> Optional[SavingsTransaction]:
        """Update a savings transaction"""
        db_transaction = db.query(SavingsTransaction).filter(
            SavingsTransaction.id == transaction_id
        ).first()

        if not db_transaction:
            return None

        # Verify account belongs to user
        account = SavingsService.get_account_by_id(db, db_transaction.account_id, user_id)
        if not account:
            return None

        update_data = transaction_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_transaction, field, value)

        db.commit()
        db.refresh(db_transaction)
        return db_transaction

    @staticmethod
    def delete_transaction(db: Session, transaction_id: int, user_id: int) -> bool:
        """Delete a savings transaction"""
        db_transaction = db.query(SavingsTransaction).filter(
            SavingsTransaction.id == transaction_id
        ).first()

        if not db_transaction:
            return False

        # Verify account belongs to user
        account = SavingsService.get_account_by_id(db, db_transaction.account_id, user_id)
        if not account:
            return False

        db.delete(db_transaction)
        db.commit()
        return True

    @staticmethod
    def calculate_account_stats(db: Session, account_id: int, user_id: int) -> dict:
        """
        Calculate statistics for a savings account:
        - Total deposits
        - Total withdrawals
        - Current value (latest value_update)
        - Profit/Loss
        - Profit/Loss percentage
        """
        # Verify account belongs to user
        account = SavingsService.get_account_by_id(db, account_id, user_id)
        if not account:
            raise HTTPException(status_code=404, detail="Savings account not found")

        # Get all transactions
        transactions = db.query(SavingsTransaction).filter(
            SavingsTransaction.account_id == account_id
        ).all()

        # Calculate deposits and withdrawals
        total_deposits = sum(
            t.amount for t in transactions if t.transaction_type == 'deposit'
        )
        total_withdrawals = sum(
            t.amount for t in transactions if t.transaction_type == 'withdrawal'
        )

        # Get latest value update
        latest_value_update = db.query(SavingsTransaction).filter(
            SavingsTransaction.account_id == account_id,
            SavingsTransaction.transaction_type == 'value_update'
        ).order_by(SavingsTransaction.transaction_date.desc()).first()

        current_value = latest_value_update.amount if latest_value_update else 0

        # Calculate net invested amount (deposits - withdrawals)
        net_invested = total_deposits - total_withdrawals

        # Calculate profit/loss
        profit_loss = current_value - net_invested

        # Calculate profit/loss percentage
        profit_loss_percentage = (
            (profit_loss / net_invested * 100) if net_invested > 0 else 0
        )

        return {
            "total_deposits": total_deposits,
            "total_withdrawals": total_withdrawals,
            "current_value": current_value,
            "net_invested": net_invested,
            "profit_loss": profit_loss,
            "profit_loss_percentage": round(profit_loss_percentage, 2),
            "transaction_count": len(transactions)
        }

    @staticmethod
    def get_accounts_with_stats(db: Session, user_id: int) -> List[dict]:
        """Get all accounts with their statistics"""
        accounts = SavingsService.get_accounts(db, user_id)
        result = []

        for account in accounts:
            stats = SavingsService.calculate_account_stats(db, account.id, user_id)
            transactions = SavingsService.get_transactions(db, account.id, user_id, limit=10)

            account_data = {
                "id": account.id,
                "user_id": account.user_id,
                "name": account.name,
                "account_type": account.account_type,
                "description": account.description,
                "is_active": account.is_active,
                "created_at": account.created_at,
                "updated_at": account.updated_at,
                **stats,
                "transactions": transactions
            }
            result.append(account_data)

        return result

    @staticmethod
    def get_portfolio_summary(db: Session, user_id: int) -> dict:
        """
        Get a summary of the entire savings portfolio for dashboard display:
        - Total portfolio value
        - Total invested
        - Total profit/loss
        - Overall profit/loss percentage
        - Number of accounts
        - Breakdown by account type
        """
        accounts = SavingsService.get_accounts(db, user_id)

        if not accounts:
            return {
                "total_value": 0,
                "total_invested": 0,
                "total_profit_loss": 0,
                "profit_loss_percentage": 0,
                "account_count": 0,
                "accounts_by_type": {}
            }

        total_value = 0
        total_invested = 0
        accounts_by_type = {}

        for account in accounts:
            stats = SavingsService.calculate_account_stats(db, account.id, user_id)

            total_value += stats["current_value"]
            total_invested += stats["net_invested"]

            # Aggregate by account type
            account_type = account.account_type
            if account_type not in accounts_by_type:
                accounts_by_type[account_type] = {
                    "count": 0,
                    "value": 0,
                    "invested": 0,
                    "profit_loss": 0
                }

            accounts_by_type[account_type]["count"] += 1
            accounts_by_type[account_type]["value"] += stats["current_value"]
            accounts_by_type[account_type]["invested"] += stats["net_invested"]
            accounts_by_type[account_type]["profit_loss"] += stats["profit_loss"]

        # Calculate overall profit/loss
        total_profit_loss = total_value - total_invested
        profit_loss_percentage = (
            (total_profit_loss / total_invested * 100) if total_invested > 0 else 0
        )

        return {
            "total_value": total_value,
            "total_invested": total_invested,
            "total_profit_loss": total_profit_loss,
            "profit_loss_percentage": round(profit_loss_percentage, 2),
            "account_count": len(accounts),
            "accounts_by_type": accounts_by_type
        }
