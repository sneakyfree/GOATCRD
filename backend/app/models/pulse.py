"""
GOATCRD Pulse Models
Credit monitoring subscriptions and alerts
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class PulseFrequency(str, enum.Enum):
    """Alert frequency settings."""
    REALTIME = "realtime"
    DAILY = "daily"
    WEEKLY = "weekly"


class PulseEventType(str, enum.Enum):
    """Types of monitored events."""
    HARD_INQUIRY = "hard_inquiry"
    BALANCE_CHANGE = "balance_change"
    NEW_ACCOUNT = "new_account"
    PAYMENT_REPORTED = "payment_reported"
    DELINQUENCY = "delinquency"
    CREDIT_SCORE_CHANGE = "credit_score_change"
    UTILIZATION_CHANGE = "utilization_change"


class PulseSubscription(BaseModel):
    """Consumer subscription to credit pulse monitoring."""
    
    __tablename__ = "pulse_subscriptions"
    
    # Consumer
    consumer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    # Settings
    frequency: Mapped[PulseFrequency] = mapped_column(
        Enum(PulseFrequency),
        default=PulseFrequency.DAILY,
        nullable=False,
    )
    
    # Event type filters (empty = all events)
    event_types: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    paused_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Consent
    consent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("consents.id"),
    )
    
    # Relationships
    consumer = relationship("User", back_populates="pulse_subscriptions")
    alerts = relationship("PulseAlert", back_populates="subscription")


class PulseAlert(BaseModel):
    """Credit pulse monitoring alert."""
    
    __tablename__ = "pulse_alerts"
    
    # Consumer and subscription
    consumer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    subscription_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pulse_subscriptions.id"),
    )
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
    )
    
    # Event
    event_type: Mapped[PulseEventType] = mapped_column(
        Enum(PulseEventType),
        nullable=False,
    )
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    
    # Content
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    impact: Mapped[str | None] = mapped_column(Text)  # e.g., "Your credit utilization improved to 23%"
    suggested_action: Mapped[str | None] = mapped_column(Text)
    
    # Data
    event_data: Mapped[dict | None] = mapped_column(JSONB)  # Raw event details
    
    # Scenario refresh
    scenario_refresh_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    scenario_refresh_triggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    consumer = relationship("User", back_populates="pulse_alerts")
    subscription = relationship("PulseSubscription", back_populates="alerts")
    case = relationship("Case", back_populates="pulse_alerts")
