"""
GOATCRD User and RBAC Models
Role-based access control with audit support
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, TimestampMixin


class UserRole(str, enum.Enum):
    """User roles per GOATCRD RBAC spec."""
    CONSUMER = "consumer"
    PRO_USER = "pro_user"
    REVIEWER = "reviewer"
    ADMIN = "admin"
    PARTNER = "partner"


class User(BaseModel):
    """User account model."""
    
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Profile
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    
    # Role
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.CONSUMER,
        nullable=False,
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Partner association (for partner users)
    partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id"),
        nullable=True,
    )
    
    # Relationships
    cases = relationship("Case", back_populates="consumer", foreign_keys="Case.consumer_id")
    consents = relationship("Consent", back_populates="consumer")
    audit_events = relationship("AuditEvent", back_populates="actor")


class Partner(BaseModel):
    """B2B Partner for Embedded Finance SDK."""
    
    __tablename__ = "partners"
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    api_key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Configuration
    allowed_programs: Mapped[str | None] = mapped_column(Text)  # JSON array of program IDs
    branding_config: Mapped[str | None] = mapped_column(Text)  # JSON
    callback_urls: Mapped[str | None] = mapped_column(Text)  # JSON
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    users = relationship("User", backref="partner")


class AuditEvent(BaseModel):
    """Append-only audit event log."""
    
    __tablename__ = "audit_events"
    
    # Actor
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True,
    )
    actor_role: Mapped[str | None] = mapped_column(String(50))
    actor_ip: Mapped[str | None] = mapped_column(String(45))  # IPv6 max length
    
    # Event
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(100))
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    
    # Data
    event_data: Mapped[str | None] = mapped_column(Text)  # JSON
    
    # Relationships
    actor = relationship("User", back_populates="audit_events")
