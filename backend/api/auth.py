"""
JWT Token Validation Middleware for auth-server-ruby integration

This module validates JWT tokens issued by the auth-server-ruby microservice.
"""

import os
import jwt
import httpx
from typing import Optional
from datetime import datetime
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel


# Security scheme for JWT tokens
security = HTTPBearer()


class TokenData(BaseModel):
    """Decoded JWT token data"""
    user_id: int
    username: str
    email: Optional[str] = None
    is_admin: bool = False
    exp: int  # Expiration timestamp


class AuthConfig:
    """Authentication configuration"""

    def __init__(self):
        # Auth server configuration
        self.AUTH_SERVER_URL = os.getenv("AUTH_SERVER_URL", "http://localhost:4567")
        self.JWT_SECRET = os.getenv("JWT_SECRET")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

        if not self.JWT_SECRET:
            raise ValueError("JWT_SECRET environment variable is required")

        if len(self.JWT_SECRET) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")

    def get_auth_server_url(self) -> str:
        """Get auth server base URL"""
        return self.AUTH_SERVER_URL


# Global config instance
config = AuthConfig()


def decode_token(token: str) -> TokenData:
    """
    Decode and validate JWT token from auth-server-ruby

    Args:
        token: JWT token string

    Returns:
        TokenData object with user information

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM]
        )

        # Extract user data from token
        token_data = TokenData(
            user_id=payload.get("user_id"),
            username=payload.get("username"),
            email=payload.get("email"),
            is_admin=payload.get("is_admin", False),
            exp=payload.get("exp")
        )

        return token_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token validation failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token

    Usage:
        @app.get("/protected")
        async def protected_route(user: TokenData = Depends(get_current_user)):
            return {"user_id": user.user_id, "username": user.username}

    Args:
        credentials: HTTP Bearer token from Authorization header

    Returns:
        TokenData object with user information

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    return decode_token(token)


async def get_current_admin_user(
    current_user: TokenData = Depends(get_current_user)
) -> TokenData:
    """
    Dependency to require admin privileges

    Usage:
        @app.get("/admin/users")
        async def admin_only(user: TokenData = Depends(get_current_admin_user)):
            return {"message": "Admin access granted"}

    Args:
        current_user: Current authenticated user

    Returns:
        TokenData object if user is admin

    Raises:
        HTTPException: If user is not an admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def verify_token_with_auth_server(token: str) -> dict:
    """
    Verify token with auth-server-ruby /profile endpoint (optional extra validation)

    This makes an HTTP request to the auth server to validate the token.
    Use this for critical operations where you want real-time validation.

    Args:
        token: JWT token string

    Returns:
        User profile data from auth server

    Raises:
        HTTPException: If token is invalid or auth server is unreachable
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{config.get_auth_server_url()}/profile",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0  # 5 second timeout
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token validation failed with auth server",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Auth server unavailable"
                )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Auth server connection error: {str(e)}"
        )


class AuthServiceClient:
    """Client for interacting with auth-server-ruby microservice"""

    def __init__(self):
        self.base_url = config.get_auth_server_url()

    async def health_check(self) -> dict:
        """Check if auth server is healthy"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.json()
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

    async def register_user(self, username: str, email: str, password: str) -> dict:
        """
        Register new user via auth server

        Args:
            username: User's username
            email: User's email
            password: User's password

        Returns:
            Registration response from auth server
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/register",
                json={
                    "username": username,
                    "email": email,
                    "password": password
                },
                timeout=10.0
            )

            if response.status_code == 201:
                return response.json()
            else:
                error_data = response.json()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("error", "Registration failed")
                )

    async def login_user(self, username: str, password: str) -> dict:
        """
        Login user via auth server

        Args:
            username: Username or email
            password: User's password

        Returns:
            Login response with JWT token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=10.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                raise HTTPException(
                    status_code=response.status_code,
                    detail=error_data.get("error", "Login failed")
                )


# Global auth service client instance
auth_service = AuthServiceClient()
