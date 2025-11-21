from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.schemas import (
    SavingsAccountCreate,
    SavingsAccountUpdate,
    SavingsAccountResponse,
    SavingsAccountWithStats,
    SavingsTransactionCreate,
    SavingsTransactionUpdate,
    SavingsTransactionResponse
)
from app.services.savings_service import SavingsService

router = APIRouter(prefix="/savings", tags=["savings"])


# Savings Account Endpoints
@router.get("/accounts", response_model=List[SavingsAccountWithStats])
def get_savings_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all savings accounts with statistics"""
    return SavingsService.get_accounts_with_stats(db, current_user.id)


@router.get("/accounts/{account_id}", response_model=SavingsAccountWithStats)
def get_savings_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific savings account with statistics"""
    account = SavingsService.get_account_by_id(db, account_id, current_user.id)
    if not account:
        raise HTTPException(status_code=404, detail="Savings account not found")

    stats = SavingsService.calculate_account_stats(db, account_id, current_user.id)
    transactions = SavingsService.get_transactions(db, account_id, current_user.id)

    return {
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


@router.post("/accounts", response_model=SavingsAccountResponse, status_code=201)
def create_savings_account(
    account: SavingsAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new savings account"""
    return SavingsService.create_account(db, account, current_user.id)


@router.put("/accounts/{account_id}", response_model=SavingsAccountResponse)
def update_savings_account(
    account_id: int,
    account_update: SavingsAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a savings account"""
    updated_account = SavingsService.update_account(
        db, account_id, account_update, current_user.id
    )
    if not updated_account:
        raise HTTPException(status_code=404, detail="Savings account not found")
    return updated_account


@router.delete("/accounts/{account_id}", status_code=204)
def delete_savings_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a savings account"""
    success = SavingsService.delete_account(db, account_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Savings account not found")
    return None


# Savings Transaction Endpoints
@router.get("/accounts/{account_id}/transactions", response_model=List[SavingsTransactionResponse])
def get_account_transactions(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all transactions for a savings account"""
    return SavingsService.get_transactions(db, account_id, current_user.id)


@router.post("/transactions", response_model=SavingsTransactionResponse, status_code=201)
def create_transaction(
    transaction: SavingsTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new transaction (deposit, withdrawal, or value update)"""
    return SavingsService.create_transaction(db, transaction, current_user.id)


@router.put("/transactions/{transaction_id}", response_model=SavingsTransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: SavingsTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a transaction"""
    updated_transaction = SavingsService.update_transaction(
        db, transaction_id, transaction_update, current_user.id
    )
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction


@router.delete("/transactions/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a transaction"""
    success = SavingsService.delete_transaction(db, transaction_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return None


@router.get("/accounts/{account_id}/stats")
def get_account_stats(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for a savings account"""
    return SavingsService.calculate_account_stats(db, account_id, current_user.id)
