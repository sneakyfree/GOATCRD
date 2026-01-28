"""
GOATCRD Fairness Model
Storage for fairness test results
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class FairnessTestStatus(str, enum.Enum):
    """Fairness test status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


class FairnessTest(BaseModel):
    """Stored fairness test result."""
    
    __tablename__ = "fairness_tests"
    
    # Version identifiers
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
    rules_version: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Status
    status: Mapped[FairnessTestStatus] = mapped_column(
        Enum(FairnessTestStatus),
        default=FairnessTestStatus.PENDING,
        nullable=False,
    )
    
    # Test results
    disparate_impact_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    feature_audit_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    lda_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Detailed results (JSON)
    disparate_impact_results: Mapped[dict | None] = mapped_column(JSONB)
    feature_audit_result: Mapped[dict | None] = mapped_column(JSONB)
    lda_result: Mapped[dict | None] = mapped_column(JSONB)
    
    # Issues
    blocking_issues: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    warnings: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[float | None] = mapped_column()
    
    # Approval workflow
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    approval_notes: Mapped[str | None] = mapped_column(Text)
    
    # Deployment gate
    deployment_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
