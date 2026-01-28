"""
GOATCRD Case and Intake Models
Core case management with intake snapshots
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, VersionedModel


class CaseStatus(str, enum.Enum):
    """Case lifecycle status."""
    DRAFT = "draft"
    INTAKE_IN_PROGRESS = "intake_in_progress"
    INTAKE_COMPLETE = "intake_complete"
    PROCESSING = "processing"
    SCENARIOS_READY = "scenarios_ready"
    REVIEW_REQUIRED = "review_required"
    EXPORTED = "exported"
    CLOSED = "closed"


class Case(BaseModel):
    """Main case entity representing a consumer credit evaluation."""
    
    __tablename__ = "cases"
    
    # Consumer
    consumer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    
    # Partner context (for embedded finance)
    partner_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("partners.id"),
        nullable=True,
    )
    
    # Status
    status: Mapped[CaseStatus] = mapped_column(
        Enum(CaseStatus),
        default=CaseStatus.DRAFT,
        nullable=False,
    )
    
    # Metadata
    case_type: Mapped[str | None] = mapped_column(String(50))  # personal_loan, credit_card, etc.
    
    # Relationships
    consumer = relationship("User", back_populates="cases", foreign_keys=[consumer_id])
    intake_drafts = relationship("IntakeDraft", back_populates="case")
    intake_snapshots = relationship("IntakeSnapshot", back_populates="case")
    consents = relationship("Consent", back_populates="case")
    scenario_runs = relationship("ScenarioRun", back_populates="case")
    review_tickets = relationship("ReviewTicket", back_populates="case")
    audit_snapshots = relationship("AuditSnapshot", back_populates="case")


class Invite(BaseModel):
    """Secure invite link for mobile-first intake."""
    
    __tablename__ = "invites"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
    )
    
    # Token
    token_hash: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    
    # Validity
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Contact
    sent_to_email: Mapped[str | None] = mapped_column(String(255))
    sent_to_phone: Mapped[str | None] = mapped_column(String(20))


class IntakeDraft(BaseModel):
    """Work-in-progress intake data (save/resume)."""
    
    __tablename__ = "intake_drafts"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
    )
    
    # Draft data
    data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Progress
    current_chapter: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    completed_chapters: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Validation
    contradictions: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    missing_fields: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Relationships
    case = relationship("Case", back_populates="intake_drafts")


class IntakeSnapshot(VersionedModel):
    """Immutable snapshot of intake data at a point in time."""
    
    __tablename__ = "intake_snapshots"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
        index=True,
    )
    
    # Raw and normalized data
    raw_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    normalized_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Provenance
    provenance: Mapped[dict] = mapped_column(JSONB, nullable=False)  # field -> provenance record
    
    # Validation state at snapshot time
    contradictions_resolved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    case = relationship("Case", back_populates="intake_snapshots")
