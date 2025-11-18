"""
FastAPI Dependencies for Dependency Injection

This module provides reusable dependencies for:
- Database sessions
- Authentication/Authorization
- Rate limiting
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import os

# Import database session (will use existing agent.models)
# from agent.models import get_session

security = HTTPBearer()


# Database Dependency
def get_db():
    """
    Dependency to get database session.
    Yields a database session and ensures it's closed after use.
    """
    # Import here to avoid circular imports
    from agent.models import get_session

    db = get_session()
    try:
        yield db
    finally:
        db.close()


# Authentication Dependency (placeholder - will implement with JWT)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Dependency to get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials

    # TODO: Implement JWT verification
    # from api.services.auth_service import verify_token
    # user_id = verify_token(token)

    # Temporary: Always return None until auth is implemented
    # This allows us to test other endpoints without auth

    # TODO: Query user from database
    # from agent.models import User
    # user = db.query(User).filter(User.id == user_id).first()
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="User not found"
    #     )
    # return user

    # Placeholder return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication not yet implemented",
        headers={"WWW-Authenticate": "Bearer"},
    )


# Optional Authentication (for public endpoints that can work with/without auth)
async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Dependency to optionally get current authenticated user.
    Returns None if no valid token is provided.
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    try:
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=authorization.replace("Bearer ", "")
        )
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


# Rate Limiting Dependency (placeholder)
async def check_rate_limit(
    request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Dependency to check rate limits.

    Rate limits:
    - Authenticated users: 100 requests/minute
    - Unauthenticated: 10 requests/minute
    """
    # TODO: Implement rate limiting with Redis
    # For now, just pass through
    pass


# Admin User Dependency
async def get_current_admin_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency to require admin privileges.

    Raises:
        HTTPException: If user is not an admin
    """
    # TODO: Check if user has admin role
    # if not current_user.is_admin:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin privileges required"
    #     )
    return current_user
