"""
GOATCRD Pydantic Schemas - User and Auth
"""
from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, IDSchema, TimestampSchema


class UserBase(BaseSchema):
    """Base user schema."""
    
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class UserCreate(UserBase):
    """User creation schema."""
    
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    """User update schema."""
    
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class UserResponse(UserBase, IDSchema, TimestampSchema):
    """User response schema."""
    
    role: str
    is_active: bool
    is_verified: bool
    partner_id: UUID | None = None


class UserInDB(UserResponse):
    """User with hashed password (internal use)."""
    
    hashed_password: str


# Auth schemas
class Token(BaseSchema):
    """JWT token response."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseSchema):
    """JWT token payload."""
    
    sub: UUID
    role: str
    exp: datetime


class LoginRequest(BaseSchema):
    """Login request schema."""
    
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseSchema):
    """Refresh token request."""
    
    refresh_token: str
