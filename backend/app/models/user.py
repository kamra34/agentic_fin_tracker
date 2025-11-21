from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    currency = Column(String(10), default="SEK")
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Personal finance metrics
    household_members = Column(Integer, nullable=True)
    num_vehicles = Column(Integer, nullable=True)
    housing_type = Column(String(50), nullable=True)
    house_size_sqm = Column(Integer, nullable=True)
    monthly_income_goal = Column(Float, nullable=True)
    monthly_savings_goal = Column(Float, nullable=True)

    expenses = relationship("Expense", back_populates="user")
    accounts = relationship("Account", back_populates="user")
    categories = relationship("Category", back_populates="user")
    income_templates = relationship("IncomeTemplate", back_populates="user")
    monthly_incomes = relationship("MonthlyIncome", back_populates="user")
    expense_templates = relationship("ExpenseTemplate", back_populates="user")
    savings_accounts = relationship("SavingsAccount", back_populates="user")
