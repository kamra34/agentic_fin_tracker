from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.schemas import DashboardStats
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.services.income_service import IncomeService
from app.services.expense_template_service import ExpenseTemplateService
from app.services.analytics_service import AnalyticsService
from app.services.savings_service import SavingsService

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the current user"""
    service = DashboardService(db)
    return service.get_stats(current_user.id)


@router.get("/initial-data")
async def get_dashboard_initial_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all dashboard data in a single request - reduces network round-trips"""
    dashboard_service = DashboardService(db)
    income_service = IncomeService(db)
    expense_service = ExpenseTemplateService(db)
    savings_service = SavingsService()

    return {
        "stats": dashboard_service.get_stats(current_user.id),
        "income_templates": income_service.get_templates(current_user.id),
        "expense_templates": expense_service.get_templates_with_names(current_user.id),
        "savings_summary": savings_service.get_portfolio_summary(db, current_user.id)
    }


@router.get("/expense-analytics")
async def get_expense_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive expense analytics across multiple time windows"""
    service = AnalyticsService(db)
    return service.get_expense_analytics(current_user.id)


@router.get("/expense-analytics-detail")
async def get_expense_analytics_detail(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed expense analytics for the deep-dive page"""
    service = AnalyticsService(db)
    return service.get_expense_analysis_detail(current_user.id)
