from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.schemas import (
    IncomeTemplateCreate, IncomeTemplateUpdate, IncomeTemplateResponse,
    MonthlyIncomeCreate, MonthlyIncomeUpdate, MonthlyIncomeResponse
)
from app.services.income_service import IncomeService
from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/incomes", tags=["incomes"])


# ========== TEMPLATE ENDPOINTS ==========

@router.get("/templates", response_model=List[IncomeTemplateResponse])
def get_income_templates(
    include_inactive: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all income templates (recurring income sources)"""
    service = IncomeService(db)
    return service.get_templates(current_user.id, include_inactive)


@router.get("/templates/{template_id}", response_model=IncomeTemplateResponse)
def get_income_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific income template"""
    service = IncomeService(db)
    template = service.get_template_by_id(template_id, current_user.id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income template not found"
        )
    return template


@router.post("/templates", response_model=IncomeTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_income_template(
    template: IncomeTemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new income template (recurring income source)"""
    service = IncomeService(db)
    return service.create_template(template, current_user.id)


@router.put("/templates/{template_id}", response_model=IncomeTemplateResponse)
def update_income_template(
    template_id: int,
    template_update: IncomeTemplateUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an income template"""
    service = IncomeService(db)
    updated = service.update_template(template_id, current_user.id, template_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income template not found"
        )
    return updated


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an income template (soft delete)"""
    service = IncomeService(db)
    success = service.delete_template(template_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income template not found"
        )


# ========== MONTHLY INCOME ENDPOINTS ==========

@router.get("/monthly", response_model=List[MonthlyIncomeResponse])
def get_monthly_incomes(
    month: Optional[str] = Query(None, description="Filter by month (format: YYYY-MM)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly income entries"""
    service = IncomeService(db)
    return service.get_monthly_incomes(current_user.id, month)


@router.get("/monthly/{income_id}", response_model=MonthlyIncomeResponse)
def get_monthly_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific monthly income entry"""
    service = IncomeService(db)
    income = service.get_monthly_income_by_id(income_id, current_user.id)
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monthly income not found"
        )
    return income


@router.post("/monthly", response_model=MonthlyIncomeResponse, status_code=status.HTTP_201_CREATED)
def create_monthly_income(
    income: MonthlyIncomeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new monthly income entry (one-time or from template)"""
    service = IncomeService(db)
    return service.create_monthly_income(income, current_user.id)


@router.put("/monthly/{income_id}", response_model=MonthlyIncomeResponse)
def update_monthly_income(
    income_id: int,
    income_update: MonthlyIncomeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a monthly income entry"""
    service = IncomeService(db)
    updated = service.update_monthly_income(income_id, current_user.id, income_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monthly income not found"
        )
    return updated


@router.delete("/monthly/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monthly_income(
    income_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a monthly income entry"""
    service = IncomeService(db)
    success = service.delete_monthly_income(income_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monthly income not found"
        )


# ========== UTILITY ENDPOINTS ==========

@router.post("/generate/{month}", response_model=List[MonthlyIncomeResponse])
def generate_monthly_incomes(
    month: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate monthly income entries from active templates for a specific month.
    Only creates entries that don't already exist.
    Format: YYYY-MM
    """
    service = IncomeService(db)
    return service.generate_monthly_incomes(current_user.id, month)


@router.get("/total/{month}")
def get_monthly_total(
    month: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get total income for a specific month"""
    service = IncomeService(db)
    total = service.get_monthly_total(current_user.id, month)
    return {"month": month, "total": total}


@router.get("/by-source")
def get_income_by_source(
    month: Optional[str] = Query(None, description="Filter by month (format: YYYY-MM)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get income grouped by source"""
    service = IncomeService(db)
    return service.get_income_by_source(current_user.id, month)
