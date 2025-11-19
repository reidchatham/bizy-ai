"""
Authentication Proxy Routes

Proxy routes to auth-server-ruby microservice for authentication operations.
These routes allow the frontend to interact with auth through the main API.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from api.auth import auth_service, get_current_user, TokenData


router = APIRouter()


# Request/Response Models
class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)


class LoginRequest(BaseModel):
    """User login request"""
    username: str  # Can be username or email
    password: str


class LoginResponse(BaseModel):
    """User login response"""
    message: str
    token: str
    user: dict


class UserProfileResponse(BaseModel):
    """User profile response"""
    id: int
    username: str
    email: str
    is_admin: bool
    email_verified: bool


# Routes

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Register a new user via auth-server-ruby

    Creates a new user account and sends email verification.

    Args:
        request: Registration details (username, email, password)

    Returns:
        User object and success message

    Raises:
        400: Validation errors (weak password, duplicate email, etc.)
        503: Auth server unavailable
    """
    result = await auth_service.register_user(
        username=request.username,
        email=request.email,
        password=request.password
    )
    return result


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Login user and receive JWT token

    Authenticates user and returns JWT token for subsequent requests.

    Args:
        request: Login credentials (username/email and password)

    Returns:
        JWT token and user profile

    Raises:
        401: Invalid credentials or unverified email
        423: Account locked (too many failed attempts)
        503: Auth server unavailable
    """
    result = await auth_service.login_user(
        username=request.username,
        password=request.password
    )
    return result


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(current_user: TokenData = Depends(get_current_user)):
    """
    Get current user's profile

    Returns the authenticated user's profile information.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        User profile data

    Raises:
        401: Missing or invalid token
    """
    return {
        "id": current_user.user_id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "email_verified": True  # If token is valid, email is verified
    }


@router.post("/logout")
async def logout(current_user: TokenData = Depends(get_current_user)):
    """
    Logout user

    Client-side logout (token removal).
    Server doesn't track tokens, so this just confirms authentication.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        Success message
    """
    return {
        "message": "Logged out successfully",
        "username": current_user.username
    }


@router.get("/verify-token")
async def verify_token(current_user: TokenData = Depends(get_current_user)):
    """
    Verify that JWT token is valid

    Used by frontend to check if user is still authenticated.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        Token validity and user info

    Raises:
        401: Invalid or expired token
    """
    return {
        "valid": True,
        "user": {
            "id": current_user.user_id,
            "username": current_user.username,
            "is_admin": current_user.is_admin
        }
    }


@router.get("/auth-server-health")
async def auth_server_health():
    """
    Check auth server health

    Useful for monitoring and troubleshooting.

    Returns:
        Auth server health status
    """
    health = await auth_service.health_check()
    return {
        "auth_server": health
    }
