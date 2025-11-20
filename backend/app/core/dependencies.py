from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.schemas import TokenData
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Cache for user lookups - keeps users in memory for 10 minutes
# Max 1000 users to prevent memory issues
user_cache = TTLCache(maxsize=1000, ttl=600)  # 10 minutes TTL


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token with caching"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    # Check cache first
    if email in user_cache:
        logger.info(f"⚡ User cache HIT for {email}")
        return user_cache[email]

    # Cache miss - query database
    logger.info(f"🔍 User cache MISS for {email} - querying database")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    # Store in cache for future requests
    user_cache[email] = user
    logger.info(f"💾 Cached user {email} for 10 minutes")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current superuser"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user
