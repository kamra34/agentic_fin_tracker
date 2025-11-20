from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)

    # Old text columns (kept for backup)
    category = Column(String(50), nullable=True)
    subcategory = Column(String(50), nullable=True)

    # New foreign key columns
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    subcategory_id = Column(Integer, ForeignKey("subcategories.id"), nullable=True)

    amount = Column(Float, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Boolean, nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    user = relationship("User", back_populates="expenses")
    account = relationship("Account", back_populates="expenses")
    category_obj = relationship("Category", back_populates="expenses")
    subcategory_obj = relationship("Subcategory", back_populates="expenses")
