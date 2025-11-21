from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.schemas import (
    ExpenseCreate, ExpenseUpdate, ExpenseResponse, MonthlyAccountAllocation,
    ExpenseTemplateCreate, ExpenseTemplateUpdate, ExpenseTemplateResponse
)
from app.models.user import User
from app.services.expense_service import ExpenseService
from app.services.expense_template_service import ExpenseTemplateService

router = APIRouter()


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new expense"""
    try:
        service = ExpenseService(db)
        return service.create_expense(expense, current_user.id)
    except Exception as e:
        print(f"Error creating expense: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[ExpenseResponse])
async def get_expenses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get expenses with optional filters"""
    service = ExpenseService(db)
    return service.get_expenses(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        category=category,
        start_date=start_date,
        end_date=end_date,
        status=status
    )


@router.get("/categories", response_model=List[str])
async def get_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all unique categories for the user"""
    service = ExpenseService(db)
    return service.get_categories(current_user.id)


@router.get("/subcategories", response_model=List[str])
async def get_subcategories(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all unique subcategories for the user"""
    service = ExpenseService(db)
    return service.get_subcategories(current_user.id, category)


# ========== EXPENSE TEMPLATE ENDPOINTS ==========
# NOTE: These must come BEFORE /{expense_id} route to avoid path conflicts

@router.get("/templates", response_model=List[ExpenseTemplateResponse])
async def get_expense_templates(
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all expense templates (recurring expenses)"""
    service = ExpenseTemplateService(db)
    templates = service.get_templates_with_names(current_user.id, include_inactive)
    return templates


@router.post("/templates", response_model=ExpenseTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_expense_template(
    template: ExpenseTemplateCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new expense template (recurring expense)"""
    service = ExpenseTemplateService(db)
    return service.create_template(template, current_user.id)


@router.get("/templates/{template_id}", response_model=ExpenseTemplateResponse)
async def get_expense_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense template"""
    service = ExpenseTemplateService(db)
    template = service.get_template_by_id(template_id, current_user.id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense template not found"
        )
    return template


@router.put("/templates/{template_id}", response_model=ExpenseTemplateResponse)
async def update_expense_template(
    template_id: int,
    template_update: ExpenseTemplateUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an expense template"""
    service = ExpenseTemplateService(db)
    updated = service.update_template(template_id, current_user.id, template_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense template not found"
        )
    return updated


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense_template(
    template_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an expense template (soft delete)"""
    service = ExpenseTemplateService(db)
    success = service.delete_template(template_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense template not found"
        )


# ========== INDIVIDUAL EXPENSE ENDPOINTS ==========

@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific expense"""
    service = ExpenseService(db)
    expense = service.get_expense_by_id(expense_id, current_user.id)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update an expense"""
    service = ExpenseService(db)
    expense = service.update_expense(expense_id, current_user.id, expense_update)
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an expense"""
    service = ExpenseService(db)
    success = service.delete_expense(expense_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found"
        )
    return None


@router.get("/monthly/list", response_model=List[ExpenseResponse])
async def get_monthly_expenses(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all expenses for a specific month"""
    service = ExpenseService(db)
    return service.get_monthly_expenses(current_user.id, year, month)


@router.get("/monthly/summary")
async def get_monthly_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get summary statistics for a specific month"""
    service = ExpenseService(db)
    return service.get_monthly_summary(current_user.id, year, month)


@router.get("/monthly/available")
async def get_available_months(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of year/month combinations that have expenses"""
    service = ExpenseService(db)
    return service.get_available_months(current_user.id)


@router.get("/monthly/initial-data")
async def get_monthly_initial_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all initial data needed for monthly expenses page - reduces network round-trips from 3 to 1"""
    from app.services.category_service import CategoryService
    from app.models.account import Account

    expense_service = ExpenseService(db)
    category_service = CategoryService(db)

    # Query accounts directly (no separate service)
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()

    return {
        "months": expense_service.get_available_months(current_user.id),
        "categories": category_service.get_categories(current_user.id),
        "accounts": accounts
    }


@router.get("/categories/structured")
async def get_categories_structured(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get categories with their subcategories and statistics"""
    service = ExpenseService(db)
    return service.get_categories_with_subcategories(current_user.id)


@router.get("/monthly/account-allocation", response_model=MonthlyAccountAllocation)
async def get_monthly_account_allocation(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get monthly expenses grouped by payment account"""
    service = ExpenseService(db)
    return service.get_monthly_account_allocation(current_user.id, year, month)


@router.get("/monthly/all-data")
async def get_monthly_all_data(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all monthly data in a single request - reduces network round-trips from 5 to 1"""
    from app.services.income_service import IncomeService

    expense_service = ExpenseService(db)
    income_service = IncomeService(db)

    month_str = f"{year}-{month:02d}"

    return {
        "expenses": expense_service.get_monthly_expenses(current_user.id, year, month),
        "summary": expense_service.get_monthly_summary(current_user.id, year, month),
        "allocation": expense_service.get_monthly_account_allocation(current_user.id, year, month),
        "incomes": income_service.get_monthly_incomes(current_user.id, month_str),
        "income_total": {"total": income_service.get_monthly_total(current_user.id, month_str)}
    }


# ========== GENERATE FROM TEMPLATES ==========

@router.post("/generate/{year}/{month}", response_model=List[ExpenseResponse])
async def generate_monthly_expenses(
    year: int,
    month: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate monthly expenses from active templates"""
    service = ExpenseTemplateService(db)
    created_expenses = service.generate_monthly_expenses(current_user.id, year, month)

    # Convert to response format with names
    expense_service = ExpenseService(db)
    response_expenses = []
    for expense in created_expenses:
        response = expense_service.get_expense_by_id(expense.id, current_user.id)
        response_expenses.append(response)

    return response_expenses
