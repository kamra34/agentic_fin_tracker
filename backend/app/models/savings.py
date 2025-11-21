from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"  # Money added to savings
    WITHDRAWAL = "withdrawal"  # Money taken out
    VALUE_UPDATE = "value_update"  # Current value update (for calculating profit/loss)


class SavingsAccount(Base):
    """
    Represents a savings/investment account
    Examples: Avanza, Binance, Bank Savings Account, etc.
    """
    __tablename__ = "savings_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Avanza ISK", "Binance", "Nordea Savings"
    account_type = Column(String(50), nullable=False)  # e.g., "investment", "crypto", "bank_savings"
    description = Column(String(255), nullable=True)  # Optional notes
    is_active = Column(Integer, default=1)  # 1 = active, 0 = inactive
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="savings_accounts")
    transactions = relationship("SavingsTransaction", back_populates="account", cascade="all, delete-orphan")


class SavingsTransaction(Base):
    """
    Represents transactions in a savings account
    - Deposits: Money you add to the account
    - Withdrawals: Money you take out
    - Value Updates: Current market value updates for profit/loss calculation
    """
    __tablename__ = "savings_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("savings_accounts.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # deposit, withdrawal, value_update
    amount = Column(Float, nullable=False)  # Amount deposited/withdrawn or current value
    transaction_date = Column(DateTime, nullable=False)
    notes = Column(String(255), nullable=True)  # Optional description
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    account = relationship("SavingsAccount", back_populates="transactions")
