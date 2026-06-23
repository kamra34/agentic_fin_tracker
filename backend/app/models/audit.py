from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base


class LoginEvent(Base):
    """One row per login attempt (success or failure) — the admin session/security log."""
    __tablename__ = "login_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # null for failed unknown-email
    email = Column(String(255), nullable=True)        # what was attempted (kept even if user_id is null)
    success = Column(Boolean, default=True, nullable=False)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(String(512), nullable=True)   # raw UA
    device = Column(String(128), nullable=True)        # parsed "Chrome on Windows"
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ActivityEvent(Base):
    """One row per authenticated API request — approximates 'where they went'."""
    __tablename__ = "activity_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    method = Column(String(10), nullable=True)
    path = Column(String(255), nullable=True)
    status_code = Column(Integer, nullable=True)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
