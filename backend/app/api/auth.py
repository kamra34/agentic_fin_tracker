from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.core.dependencies import get_current_active_user
from app.core.useragent import parse_device
from app.models.schemas import Token, UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.models.user import User
from app.models.audit import LoginEvent

router = APIRouter()


def _record_login(db: Session, request: Request, *, user, email: str, success: bool):
    """Best-effort login audit row; never let logging break the login flow."""
    try:
        xff = request.headers.get("x-forwarded-for")
        ip = xff.split(",")[0].strip() if xff else (request.client.host if request.client else None)
        ua = request.headers.get("user-agent", "") or ""
        db.add(LoginEvent(
            user_id=user.id if user else None,
            email=(email or "")[:255] or None,
            success=success,
            ip_address=(ip or "")[:64] or None,
            user_agent=ua[:512] or None,
            device=parse_device(ua)[:128],
        ))
        if user and success:
            user.last_login = datetime.utcnow()
        db.commit()
    except Exception:
        db.rollback()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    service = UserService(db)

    # Check if user already exists
    existing_user = service.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    return service.create_user(user)


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    service = UserService(db)

    user = service.authenticate_user(form_data.username, form_data.password)
    if not user:
        _record_login(db, request, user=None, email=form_data.username, success=False)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        _record_login(db, request, user=user, email=user.email, success=False)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    _record_login(db, request, user=user, email=user.email, success=True)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information"""
    return current_user


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    service = UserService(db)
    return service.update_user(current_user.id, user_update)
