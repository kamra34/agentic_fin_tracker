from pydantic import BaseModel, Field, EmailStr, field_validator
from datetime import datetime, date
from typing import Optional, List


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    currency: str = "SEK"


class UserCreate(UserBase):
    password: str = Field(..., min_length=4)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    currency: Optional[str] = None
    password: Optional[str] = Field(None, min_length=4)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Expense Schemas
class ExpenseBase(BaseModel):
    date: date
    category_id: int
    subcategory_id: Optional[int] = None
    amount: Optional[float] = Field(None, ge=0)
    status: Optional[bool] = True
    account_id: Optional[int] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    amount: Optional[float] = Field(None, ge=0)
    status: Optional[bool] = None
    account_id: Optional[int] = None


class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    date: date
    category_id: int
    subcategory_id: Optional[int] = None
    amount: Optional[float]
    status: Optional[bool]
    account_id: Optional[int]
    # Include category names for display
    category_name: Optional[str] = None
    subcategory_name: Optional[str] = None

    class Config:
        from_attributes = True


# Dashboard Schemas
class DashboardStats(BaseModel):
    total_expenses: float
    expense_count: int
    active_expense_count: int
    categories_summary: dict


class CategorySummary(BaseModel):
    category: str
    total_amount: float
    count: int


# Category Schemas
class SubcategoryBase(BaseModel):
    name: str
    is_active: bool = True


class SubcategoryCreate(SubcategoryBase):
    category_id: int


class SubcategoryResponse(SubcategoryBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    subcategories: List[SubcategoryResponse] = []

    class Config:
        from_attributes = True


class CategoryWithStats(CategoryResponse):
    expense_count: int
    total_amount: float
