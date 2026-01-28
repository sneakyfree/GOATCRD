"""
GOATCRD Program and Ruleset Models
Versioned program catalog with governance
"""
import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, VersionedModel


class ProgramType(str, enum.Enum):
    """Credit program types."""
    PERSONAL_LOAN = "personal_loan"
    CREDIT_CARD = "credit_card"
    MORTGAGE = "mortgage"
    AUTO_LOAN = "auto_loan"
    HELOC = "heloc"
    STUDENT_LOAN = "student_loan"


class PricingSourceType(str, enum.Enum):
    """Source of pricing information."""
    API = "api"
    MANUAL = "manual"
    ESTIMATE = "estimate"
    UNKNOWN = "unknown"


class Program(VersionedModel):
    """Credit program definition."""
    
    __tablename__ = "programs"
    
    # Identity
    program_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Type and provider
    program_type: Mapped[ProgramType] = mapped_column(Enum(ProgramType), nullable=False)
    provider_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    provider_name: Mapped[str | None] = mapped_column(String(255))
    
    # Geography
    geography_constraints: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Rules
    eligibility_ruleset_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rulesets.id"),
    )
    
    # Pricing
    pricing_source: Mapped[PricingSourceType] = mapped_column(
        Enum(PricingSourceType),
        default=PricingSourceType.UNKNOWN,
        nullable=False,
    )
    
    # Documentation
    required_docs: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    disclosures: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    
    # Lifecycle
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    deprecated_date: Mapped[date | None] = mapped_column(Date)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    eligibility_ruleset = relationship("Ruleset", foreign_keys=[eligibility_ruleset_id])
    scenarios = relationship("Scenario", back_populates="program")


class Ruleset(VersionedModel):
    """Configurable rules for eligibility/triage."""
    
    __tablename__ = "rulesets"
    
    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    
    # Rules
    rules_json: Mapped[dict] = mapped_column(JSONB, nullable=False)  # YAML/JSON compiled rules
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    programs = relationship("Program", back_populates="eligibility_ruleset", foreign_keys=[Program.eligibility_ruleset_id])


class ReasonCodeMap(VersionedModel):
    """Mapping from rule hits to adverse-action-safe reason codes."""
    
    __tablename__ = "reason_code_maps"
    
    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Mapping
    mappings: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Format: {"rule_hit_code": {"reason_code": "RC001", "category": "...", "description": "..."}}
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ReasonCode(BaseModel):
    """Adverse-action-safe reason code definitions."""
    
    __tablename__ = "reason_codes"
    
    # Code
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    
    # Content
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    consumer_message: Mapped[str] = mapped_column(Text, nullable=False)  # Plain language
    what_can_improve: Mapped[str | None] = mapped_column(Text)  # Directional guidance
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
