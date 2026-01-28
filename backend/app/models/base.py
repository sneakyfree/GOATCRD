"""
GOATCRD Database Models - Base and Mixins
Common patterns for all models
"""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Mixin for UUID primary key."""
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class VersionMixin:
    """Mixin for versioned entities."""
    
    version: Mapped[int] = mapped_column(default=1, nullable=False)


class AuditMixin:
    """Mixin for audit tracking."""
    
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Base model with UUID and timestamps."""
    
    __abstract__ = True


class VersionedModel(BaseModel, VersionMixin, AuditMixin):
    """Versioned model with audit tracking."""
    
    __abstract__ = True
