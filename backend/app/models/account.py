from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    owner_name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)  # Index for user queries
    # Optional: this account's income/expenses count toward the OWNER of this funding
    # account in the per-person budget-left view (e.g. SHARED funded by Kamiar's account).
    # NULL = the account counts under its own owner_name.
    funded_by_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    user = relationship("User", back_populates="accounts")
    expenses = relationship("Expense", back_populates="account")
