from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.core.database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # income or expense
    icon = Column(String, nullable=True)
    color = Column(String, nullable=True)

    transactions = relationship("Transaction", back_populates="category")
