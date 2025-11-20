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


class ExpenseCreate(ExpenseBase):
    account_id: int = Field(..., description="Payment account from which expense is deducted (required)")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2025-01-15",
                "category_id": 1,
                "subcategory_id": 1,
                "amount": 100.0,
                "status": True,
                "account_id": 1
            }
        }


class ExpenseUpdate(BaseModel):
    date: Optional[date] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    amount: Optional[float] = Field(None, ge=0)
    status: Optional[bool] = None
    account_id: Optional[int] = Field(None, description="Payment account from which expense is deducted")


class ExpenseResponse(BaseModel):
    id: int
    user_id: int
    date: date
    category_id: int
    subcategory_id: Optional[int] = None
    amount: Optional[float]
    status: Optional[bool]
    account_id: Optional[int] = Field(None, description="Payment account (optional for backward compatibility with old data)")
    # Include names for display
    category_name: Optional[str] = None
    subcategory_name: Optional[str] = None
    account_name: Optional[str] = None

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


# Monthly Account Allocation Schemas
class AccountAllocation(BaseModel):
    account_id: Optional[int]
    account_name: Optional[str]
    owner_name: Optional[str]
    total_amount: float
    expense_count: int


class MonthlyAccountAllocation(BaseModel):
    year: int
    month: int
    total_expenses: float
    allocations: List[AccountAllocation]


# Category Schemas
class SubcategoryBase(BaseModel):
    name: str
    is_active: bool = True


class SubcategoryCreate(SubcategoryBase):
    category_id: int


class SubcategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class SubcategoryResponse(SubcategoryBase):
    id: int
    category_id: int

    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    category_type: str = 'expense'  # expense, income, saving
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    category_type: Optional[str] = None
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


# Payment Account Schemas
class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Payment account name (e.g., 'Main Bank Account', 'Credit Card')")
    owner_name: str = Field(..., min_length=1, max_length=100, description="Account owner name")


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    owner_name: Optional[str] = Field(None, min_length=1, max_length=100)


class AccountResponse(AccountBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class AccountWithStats(AccountResponse):
    expense_count: int
    total_amount: float


# Income Template Schemas (Recurring income sources)
class IncomeTemplateBase(BaseModel):
    source_name: str = Field(..., min_length=1, max_length=100)
    current_amount: float = Field(..., gt=0)


class IncomeTemplateCreate(IncomeTemplateBase):
    pass


class IncomeTemplateUpdate(BaseModel):
    source_name: Optional[str] = Field(None, min_length=1, max_length=100)
    current_amount: Optional[float] = Field(None, gt=0)
    is_active: Optional[bool] = None


class IncomeTemplateResponse(IncomeTemplateBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Monthly Income Schemas (Actual income entries per month)
class MonthlyIncomeBase(BaseModel):
    month: str = Field(..., pattern=r'^\d{4}-\d{2}$')  # Format: YYYY-MM
    source_name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    is_one_time: bool = False
    description: Optional[str] = Field(None, max_length=255)


class MonthlyIncomeCreate(BaseModel):
    month: str = Field(..., pattern=r'^\d{4}-\d{2}$')
    template_id: Optional[int] = None  # If from template
    source_name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    is_one_time: bool = False
    description: Optional[str] = Field(None, max_length=255)


class MonthlyIncomeUpdate(BaseModel):
    source_name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = Field(None, max_length=255)


class MonthlyIncomeResponse(MonthlyIncomeBase):
    id: int
    user_id: int
    template_id: Optional[int]

    class Config:
        from_attributes = True


# Expense Template Schemas
class ExpenseTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    category_id: int
    subcategory_id: Optional[int] = None
    account_id: Optional[int] = None


class ExpenseTemplateCreate(ExpenseTemplateBase):
    pass


class ExpenseTemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    account_id: Optional[int] = None
    is_active: Optional[bool] = None


class ExpenseTemplateResponse(ExpenseTemplateBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Include names for display
    category_name: Optional[str] = None
    subcategory_name: Optional[str] = None
    account_name: Optional[str] = None

    class Config:
        from_attributes = True
