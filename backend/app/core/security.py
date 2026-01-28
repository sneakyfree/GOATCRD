"""
GOATCRD Security Module
JWT authentication, password hashing, and RBAC
"""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings
from app.schemas.user import TokenPayload

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: UUID,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "type": "access",
    }
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(
    subject: UUID,
    role: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT refresh token."""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )
    
    to_encode = {
        "sub": str(subject),
        "role": role,
        "exp": expire,
        "type": "refresh",
    }
    
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenPayload | None:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        token_data = TokenPayload(
            sub=UUID(payload["sub"]),
            role=payload["role"],
            exp=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
        return token_data
    except (JWTError, ValidationError, KeyError, ValueError):
        return None


# RBAC permission definitions
ROLE_PERMISSIONS = {
    "consumer": {
        "cases": ["create", "read_own", "update_own"],
        "intake": ["create", "read_own", "update_own"],
        "scenarios": ["read_own"],
        "exports": ["create_own", "read_own"],
        "consents": ["create", "read_own", "revoke_own"],
        "data": ["export_own"],
    },
    "pro_user": {
        "cases": ["read_assigned", "update_assigned"],
        "intake": ["read_assigned"],
        "scenarios": ["read_assigned"],
        "exports": ["create_assigned", "read_assigned"],
        "consents": ["read_assigned"],
    },
    "reviewer": {
        "cases": ["read_all", "update_all"],
        "intake": ["read_all"],
        "scenarios": ["read_all"],
        "exports": ["create_all", "read_all"],
        "review_tickets": ["read_all", "update_all", "override"],
    },
    "admin": {
        "*": ["*"],  # Full access
    },
    "partner": {
        "cases": ["create_partner", "read_partner"],
        "intake": ["create_partner", "read_partner"],
        "scenarios": ["read_partner"],
        "exports": ["create_partner", "read_partner"],
    },
}


def check_permission(role: str, resource: str, action: str) -> bool:
    """Check if a role has permission for an action on a resource."""
    if role not in ROLE_PERMISSIONS:
        return False
    
    permissions = ROLE_PERMISSIONS[role]
    
    # Admin has full access
    if "*" in permissions and "*" in permissions["*"]:
        return True
    
    # Check specific resource
    if resource in permissions:
        resource_perms = permissions[resource]
        if action in resource_perms or "*" in resource_perms:
            return True
    
    return False
