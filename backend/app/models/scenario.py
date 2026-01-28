"""
GOATCRD Scenario and Ranking Models
Scenario universe, rankings, and audit snapshots
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, VersionedModel


class EligibilityStatus(str, enum.Enum):
    """Triage status per GOATCRD spec."""
    ELIGIBLE = "eligible"
    REFER = "refer"
    NOT_ELIGIBLE = "not_eligible"


class RankingMode(str, enum.Enum):
    """Ranking modes."""
    LOWEST_PAYMENT = "lowest_payment"
    LOWEST_TOTAL_COST = "lowest_total_cost"
    FASTEST_CLOSE = "fastest_close"
    HIGHEST_CERTAINTY = "highest_certainty"
    BEST_GOAL_FIT = "best_goal_fit"


class ScenarioRun(BaseModel):
    """A single scenario generation run."""
    
    __tablename__ = "scenario_runs"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
        index=True,
    )
    
    # Input snapshot
    intake_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("intake_snapshots.id"),
        nullable=False,
    )
    
    # Version pins
    program_versions: Mapped[dict] = mapped_column(JSONB, nullable=False)  # program_id -> version
    ruleset_versions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Results
    total_scenarios: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    eligible_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    refer_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    not_eligible_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    case = relationship("Case", back_populates="scenario_runs")
    scenarios = relationship("Scenario", back_populates="scenario_run")
    rankings = relationship("Ranking", back_populates="scenario_run")


class Scenario(BaseModel):
    """Individual scenario within a run."""
    
    __tablename__ = "scenarios"
    
    scenario_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenario_runs.id"),
        nullable=False,
        index=True,
    )
    
    program_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("programs.id"),
        nullable=False,
    )
    
    # Dedup key
    dedup_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    # Status
    status: Mapped[EligibilityStatus] = mapped_column(Enum(EligibilityStatus), nullable=False)
    
    # Rule evaluation results
    rule_hits: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    missing_inputs: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    reason_codes: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Pricing (source-labeled)
    pricing: Mapped[dict | None] = mapped_column(JSONB)
    # Format: {"monthly_payment": {..., "source": "api", "confidence": 90}, ...}
    pricing_source: Mapped[str | None] = mapped_column(String(50))
    
    # Confidence
    confidence_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confidence_drivers: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    confidence_caps: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    verify_checklist: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Explainability (cached)
    explanation_consumer: Mapped[str | None] = mapped_column(Text)
    explanation_pro: Mapped[str | None] = mapped_column(Text)
    
    # Relationships
    scenario_run = relationship("ScenarioRun", back_populates="scenarios")
    program = relationship("Program", back_populates="scenarios")


class Ranking(BaseModel):
    """Ranking results for a scenario run."""
    
    __tablename__ = "rankings"
    
    scenario_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("scenario_runs.id"),
        nullable=False,
        index=True,
    )
    
    # Mode
    mode: Mapped[RankingMode] = mapped_column(Enum(RankingMode), nullable=False)
    
    # Results
    ranked_scenarios: Mapped[list] = mapped_column(JSONB, nullable=False)
    # Format: [{"scenario_id": "...", "rank": 1, "score": 95.5, "gated": false}, ...]
    
    # Gating
    gated_scenarios: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    gating_reasons: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Relationships
    scenario_run = relationship("ScenarioRun", back_populates="rankings")


class ReviewTicket(BaseModel):
    """Human review queue ticket."""
    
    __tablename__ = "review_tickets"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
        index=True,
    )
    
    # Trigger
    trigger_reason: Mapped[str] = mapped_column(String(100), nullable=False)
    trigger_details: Mapped[dict | None] = mapped_column(JSONB)
    
    # Assignment
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # Resolution
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    
    # Relationships
    case = relationship("Case", back_populates="review_tickets")
    overrides = relationship("Override", back_populates="review_ticket")


class Override(BaseModel):
    """Human override with mandatory audit."""
    
    __tablename__ = "overrides"
    
    review_ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("review_tickets.id"),
        nullable=False,
    )
    
    # Override details
    override_type: Mapped[str] = mapped_column(String(100), nullable=False)
    original_value: Mapped[dict | None] = mapped_column(JSONB)
    new_value: Mapped[dict | None] = mapped_column(JSONB)
    
    # Mandatory fields
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[dict | None] = mapped_column(JSONB)
    
    # Actor
    overridden_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    
    # Relationships
    review_ticket = relationship("ReviewTicket", back_populates="overrides")


class AuditSnapshot(VersionedModel):
    """Immutable audit snapshot for reproducibility."""
    
    __tablename__ = "audit_snapshots"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
        index=True,
    )
    
    # Snapshot data
    intake_snapshot_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    consent_states: Mapped[dict] = mapped_column(JSONB, nullable=False)
    program_versions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    ruleset_versions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    
    # Outputs
    scenario_run_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    scenarios_summary: Mapped[dict] = mapped_column(JSONB, nullable=False)
    rankings_summary: Mapped[dict] = mapped_column(JSONB, nullable=False)
    reason_codes_summary: Mapped[list] = mapped_column(JSONB, nullable=False)
    
    # Environment
    app_version: Mapped[str] = mapped_column(String(50), nullable=False)
    feature_flags: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    
    # Hash for integrity
    snapshot_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Relationships
    case = relationship("Case", back_populates="audit_snapshots")


class Export(BaseModel):
    """Generated export packets."""
    
    __tablename__ = "exports"
    
    case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cases.id"),
        nullable=False,
    )
    audit_snapshot_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("audit_snapshots.id"),
        nullable=False,
    )
    
    # Export type
    export_type: Mapped[str] = mapped_column(String(50), nullable=False)  # consumer, pro, compliance
    
    # File
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    
    # Metadata
    generated_by: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    redaction_applied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
