from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.core.database import get_db
from app.models.schemas import (
    AccountCreate, AccountUpdate, AccountResponse, AccountWithStats
)
from app.models.account import Account
from app.models.expense import Expense
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


@router.get("/", response_model=List[AccountResponse])
def get_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all accounts for the current user"""
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    return accounts


@router.get("/with-stats", response_model=List[AccountWithStats])
def get_accounts_with_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all accounts with expense statistics"""
    accounts = db.query(
        Account.id,
        Account.name,
        Account.owner_name,
        Account.user_id,
        func.count(Expense.id).label('expense_count'),
        func.coalesce(func.sum(Expense.amount), 0).label('total_amount')
    ).outerjoin(
        Expense, Account.id == Expense.account_id
    ).filter(
        Account.user_id == current_user.id
    ).group_by(
        Account.id
    ).all()

    return [
        AccountWithStats(
            id=acc.id,
            name=acc.name,
            owner_name=acc.owner_name,
            user_id=acc.user_id,
            expense_count=acc.expense_count,
            total_amount=float(acc.total_amount)
        )
        for acc in accounts
    ]


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific account"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    return account


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new account"""
    # Check if account with same name already exists for this user
    existing = db.query(Account).filter(
        Account.user_id == current_user.id,
        Account.name == account.name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this name already exists"
        )

    db_account = Account(
        name=account.name,
        owner_name=account.owner_name,
        user_id=current_user.id
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: int,
    account_update: AccountUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an account"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    # Check for duplicate name if name is being updated
    if account_update.name and account_update.name != account.name:
        existing = db.query(Account).filter(
            Account.user_id == current_user.id,
            Account.name == account_update.name,
            Account.id != account_id
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this name already exists"
            )

    # Update fields
    if account_update.name is not None:
        account.name = account_update.name
    if account_update.owner_name is not None:
        account.owner_name = account_update.owner_name

    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an account"""
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == current_user.id
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )

    # Check if account has associated expenses
    expense_count = db.query(func.count(Expense.id)).filter(
        Expense.account_id == account_id
    ).scalar()

    if expense_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete account. It has {expense_count} associated expenses. Please reassign or delete them first."
        )

    db.delete(account)
    db.commit()
