"""Security utilities for authentication and authorization."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer token scheme
bearer_scheme = HTTPBearer()


class TokenData(BaseModel):
    """JWT token payload data."""

    user_id: UUID
    email: str
    role: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token.

    Args:
        data: Token payload data
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token data

    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str | None = payload.get("user_id")
        email: str | None = payload.get("email")
        role: str | None = payload.get("role")

        if user_id is None or email is None or role is None:
            raise credentials_exception

        return TokenData(user_id=UUID(user_id), email=email, role=role)
    except JWTError:
        raise credentials_exception


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> TokenData:
    """FastAPI dependency to get current authenticated user.

    Args:
        credentials: HTTP Bearer credentials

    Returns:
        Current user token data
    """
    token = credentials.credentials
    return decode_access_token(token)


async def require_human(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """FastAPI dependency to require human user.

    NOTE: This is a placeholder. In production, this MUST query the database
    to verify users.is_human = true. JWT claims are NOT sufficient.

    Args:
        current_user: Current user from token

    Returns:
        Current user if human

    Raises:
        HTTPException: If user is not human
    """
    # TODO: Replace with database lookup
    # is_human = await db.fetch_val("SELECT is_human FROM users WHERE id = $1", current_user.user_id)
    # if not is_human:
    #     raise HTTPException(status_code=403, detail="This action requires a human user")

    # Placeholder: Assume all users are human in development
    if settings.is_production:
        raise NotImplementedError("Human verification must query database in production")

    return current_user
