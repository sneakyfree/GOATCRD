"""
GOATCRD Pydantic Schemas - Scenario and Ranking
"""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, ConfidenceScore, IDSchema, TimestampSchema


class ScenarioRunCreate(BaseSchema):
    """Trigger a new scenario run."""
    
    intake_snapshot_id: UUID


class ScenarioRunResponse(IDSchema, TimestampSchema):
    """Scenario run response."""
    
    case_id: UUID
    intake_snapshot_id: UUID
    total_scenarios: int
    eligible_count: int
    refer_count: int
    not_eligible_count: int
    started_at: datetime
    completed_at: datetime | None = None


class ScenarioResponse(IDSchema, TimestampSchema):
    """Individual scenario response."""
    
    scenario_run_id: UUID
    program_id: UUID
    status: str  # ELIGIBLE, REFER, NOT_ELIGIBLE
    
    # Rule results
    rule_hits: list[str]
    missing_inputs: list[str]
    reason_codes: list[str]
    
    # Pricing
    pricing: dict | None = None
    pricing_source: str | None = None
    
    # Confidence
    confidence_score: int
    confidence_drivers: list[str]
    confidence_caps: list[str]
    verify_checklist: list[str]
    
    # Explanations
    explanation_consumer: str | None = None
    explanation_pro: str | None = None


class ScenarioListResponse(BaseSchema):
    """List of scenarios with summary."""
    
    scenario_run_id: UUID
    total: int
    eligible: list[ScenarioResponse]
    refer: list[ScenarioResponse]
    not_eligible: list[ScenarioResponse]


class RankingRequest(BaseSchema):
    """Request ranking in a specific mode."""
    
    mode: str = Field(..., pattern="^(lowest_payment|lowest_total_cost|fastest_close|highest_certainty|best_goal_fit)$")


class RankedScenario(BaseSchema):
    """Scenario with ranking info."""
    
    scenario_id: UUID
    rank: int
    score: float
    gated: bool
    gating_reason: str | None = None


class RankingResponse(IDSchema, TimestampSchema):
    """Ranking response."""
    
    scenario_run_id: UUID
    mode: str
    ranked_scenarios: list[RankedScenario]
    gated_scenarios: list[RankedScenario]


# Counterfactual / What-If schemas
class CounterfactualRequest(BaseSchema):
    """What-If simulation request."""
    
    hypothetical_changes: dict[str, Any] = Field(
        ...,
        description="Field changes to simulate, e.g. {'credit_utilization': 0.20}"
    )


class StatusChange(BaseSchema):
    """Status change for a program."""
    
    program_id: UUID
    original_status: str
    simulated_status: str
    changed: bool


class CounterfactualResponse(BaseSchema):
    """What-If simulation response."""
    
    case_id: UUID
    hypothetical_changes: dict[str, Any]
    status_changes: list[StatusChange]
    changes_summary: list[str]
    confidence: str  # low, medium, high
    confidence_reason: str
    disclaimer: str = "This is an estimate based on hypothetical changes. Actual eligibility may vary."


# Explainability schemas
class ExplanationLayer(BaseSchema):
    """Single explanation layer."""
    
    layer: str  # consumer, pro, compliance, deep
    content: str
    field_references: list[str]


class ExplanationResponse(BaseSchema):
    """Full explanation for a scenario."""
    
    scenario_id: UUID
    layers: dict[str, ExplanationLayer]
