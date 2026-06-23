from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_superuser
from app.models.user import User
from app.models.audit import LoginEvent, ActivityEvent

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def admin_users(
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """All users with login/activity counts and last login (superuser only)."""
    users = db.query(User).order_by(User.id).all()
    result = []
    for u in users:
        login_count = db.query(func.count(LoginEvent.id)).filter(
            LoginEvent.user_id == u.id, LoginEvent.success == True  # noqa: E712
        ).scalar() or 0
        activity_count = db.query(func.count(ActivityEvent.id)).filter(
            ActivityEvent.user_id == u.id
        ).scalar() or 0
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "is_superuser": u.is_superuser,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "last_login": u.last_login,
            "login_count": login_count,
            "activity_count": activity_count,
        })
    return result


@router.get("/login-history")
def admin_login_history(
    user_id: Optional[int] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Recent login attempts (success + failure), newest first (superuser only)."""
    q = db.query(LoginEvent, User.full_name).outerjoin(User, LoginEvent.user_id == User.id)
    if user_id:
        q = q.filter(LoginEvent.user_id == user_id)
    rows = q.order_by(desc(LoginEvent.created_at)).limit(limit).all()
    return [
        {
            "id": le.id,
            "user_id": le.user_id,
            "user_name": name,
            "email": le.email,
            "success": le.success,
            "ip_address": le.ip_address,
            "device": le.device,
            "user_agent": le.user_agent,
            "created_at": le.created_at,
        }
        for le, name in rows
    ]


@router.get("/activity")
def admin_activity(
    user_id: Optional[int] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    current_user: User = Depends(get_current_superuser),
    db: Session = Depends(get_db),
):
    """Recent authenticated API requests, newest first (superuser only)."""
    q = db.query(ActivityEvent, User.full_name, User.email).outerjoin(
        User, ActivityEvent.user_id == User.id
    )
    if user_id:
        q = q.filter(ActivityEvent.user_id == user_id)
    rows = q.order_by(desc(ActivityEvent.created_at)).limit(limit).all()
    return [
        {
            "id": ae.id,
            "user_id": ae.user_id,
            "user_name": name,
            "email": email,
            "method": ae.method,
            "path": ae.path,
            "status_code": ae.status_code,
            "ip_address": ae.ip_address,
            "created_at": ae.created_at,
        }
        for ae, name, email in rows
    ]
