from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)  # Index for date range queries

    # Old text columns (kept for backup)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)

    # New foreign key columns
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True, index=True)

    amount = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Index for user queries
    status = Column(Boolean, nullable=True, index=True)  # Index for status filtering
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True, index=True)

    user = relationship("User", back_populates="expenses")
    account = relationship("Account", back_populates="expenses")
    category_obj = relationship("Category", back_populates="expenses")
    subcategory_obj = relationship("Subcategory", back_populates="expenses")


class ExpenseTemplate(Base):
    """Recurring expenses (e.g., Rent, Internet, Gym Membership)"""
    __tablename__ = "expense_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="expense_templates")
    category = relationship("Category")
    subcategory = relationship("Subcategory")
    account = relationship("Account")
