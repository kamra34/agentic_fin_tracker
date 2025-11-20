from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class IncomeTemplate(Base):
    """Recurring income sources (e.g., Your Salary, Wife's Salary)"""
    __tablename__ = "income_templates"

    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False)  # e.g., "Your Salary", "Wife's Salary"
    current_amount = Column(Float, nullable=False)  # Current/latest amount
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="income_templates")
    monthly_entries = relationship("MonthlyIncome", back_populates="template", cascade="all, delete-orphan")


class MonthlyIncome(Base):
    """Monthly income entries - tracks actual income received each month"""
    __tablename__ = "monthly_incomes"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(7), nullable=False, index=True)  # Format: "2024-08"
    template_id = Column(Integer, ForeignKey("income_templates.id"), nullable=True)  # Null for one-time incomes
    source_name = Column(String(100), nullable=False)  # Copy from template or custom for one-time
    amount = Column(Float, nullable=False)
    is_one_time = Column(Boolean, default=False)  # True for bonus, one-time payments
    description = Column(String(255), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="monthly_incomes")
    template = relationship("IncomeTemplate", back_populates="monthly_entries")
