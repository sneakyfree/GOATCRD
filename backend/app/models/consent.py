"""
GOATCRD Consent Models
1033-Native consent management with granular scope and revocation
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ConsentScope(str, enum.Enum):
    """Granular consent scopes per 1033 requirements."""
    CREDIT_REPORT = "credit_report"
    IDENTITY_VERIFICATION = "identity_verification"
    BANK_ACCOUNT_LINK = "bank_account_link"
    EMPLOYMENT_VERIFICATION = "employment_verification"
    INCOME_VERIFICATION = "income_verification"
    RENT_HISTORY = "rent_history"
    UTILITY_HISTORY = "utility_history"


class ConsentStatus(str, enum.Enum):
    """Consent lifecycle status."""
    REQUESTED = "requested"
    GRANTED = "granted"
    DENIED = "denied"
    REVOKED = "revoked"
    EXPIRED = "expired"


class AccessorType(str, enum.Enum):
    """Type of accessor for access logging."""
    USER = "user"
    SYSTEM = "system"
    PARTNER = "partner"
    AGENT = "agent"


class Consent(BaseModel):
    """Consumer consent record per data source."""
    
    __tablename__ = "consents"
    
    # Consumer and case
    consumer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=True,
    )
    
    # Scope
    scope: Mapped[ConsentScope] = mapped_column(Enum(ConsentScope), nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "experian", "plaid"
    
    # Purpose
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Status
    status: Mapped[ConsentStatus] = mapped_column(
        Enum(ConsentStatus),
        default=ConsentStatus.REQUESTED,
        nullable=False,
    )
    
    # Lifecycle
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    granted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    denied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Retention
    retention_policy_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    
    # Downstream verification
    downstream_disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    downstream_disable_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    consumer = relationship("User", back_populates="consents")
    case = relationship("Case", back_populates="consents")
    events = relationship("ConsentEvent", back_populates="consent")


class ConsentEvent(BaseModel):
    """Audit log for consent lifecycle events."""
    
    __tablename__ = "consent_events"
    
    consent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consents.id"),
        nullable=False,
        index=True,
    )
    
    # Event
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # requested, granted, revoked, etc.
    event_data: Mapped[dict | None] = mapped_column(JSONB)
    
    # Actor
    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    actor_ip: Mapped[str | None] = mapped_column(String(45))
    
    # Relationships
    consent = relationship("Consent", back_populates="events")


class AccessLog(BaseModel):
    """1033 Access Log - who accessed what consumer data, when."""
    
    __tablename__ = "access_logs"
    
    consumer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    # Accessor
    accessor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    accessor_type: Mapped[str] = mapped_column(String(50), nullable=False)  # user, system, partner
    accessor_role: Mapped[str | None] = mapped_column(String(50))
    
    # Access details
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # read, export, share
    
    # Context
    purpose: Mapped[str | None] = mapped_column(Text)
    ip_address: Mapped[str | None] = mapped_column(String(45))
