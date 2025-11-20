from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.schemas import DashboardStats
from app.models.user import User
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics for the current user"""
    service = DashboardService(db)
    return service.get_stats(current_user.id)
