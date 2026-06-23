from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db, get_readonly_db
from app.core.security import decode_access_token
from app.models.user import User
from app.models.schemas import TokenData
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = decode_access_token(token)
    if email is None:
        raise credentials_exception

    # Query database for user
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_user_readonly(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_readonly_db)
) -> User:
    """Resolve the current user on a read-only AUTOCOMMIT session.

    Identical to get_current_user, but the auth lookup does not open a lingering
    transaction. Use for endpoints that only read and may run long external calls
    (e.g. the chat/agents flow): paired with get_readonly_db, FastAPI's dependency
    cache makes the auth lookup and the endpoint share ONE AUTOCOMMIT session, so
    nothing sits 'idle in transaction' while the agents call OpenAI.
    """
    return await get_current_user(token=token, db=db)


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
