from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.models.user import User
from app.services.expense_service import ExpenseService

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


@router.get("/categories/structured")
async def get_categories_structured(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get categories with their subcategories and statistics"""
    service = ExpenseService(db)
    return service.get_categories_with_subcategories(current_user.id)
