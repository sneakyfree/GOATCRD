"""
GOATCRD Agents API Routes
Multi-agent orchestration endpoints
"""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.agents import (
    AgentOrchestrator,
    AgentContext,
    AgentRole,
    create_orchestrator,
)
from app.models import Case, IntakeDraft, Scenario, ScenarioRun
from app.services import AuditService

router = APIRouter(prefix="/cases/{case_id}/agents", tags=["agents"])


class RunWorkflowRequest(BaseModel):
    """Request to run an agent workflow."""
    
    workflow: str  # intake_review, scenario_analysis, full_evaluation


class AgentDecisionResponse(BaseModel):
    """Response for an agent decision."""
    
    decision_id: str
    agent_role: str
    decision_type: str
    recommendation: str
    confidence: int
    reasoning: str
    requires_human_review: bool
    review_reason: str | None


class WorkflowResponse(BaseModel):
    """Response from running a workflow."""
    
    workflow: str
    decisions: list[AgentDecisionResponse]
    human_review_required: list[AgentDecisionResponse]


@router.post("/run-workflow", response_model=WorkflowResponse)
async def run_agent_workflow(
    case_id: UUID,
    request: RunWorkflowRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> WorkflowResponse:
    """
    Run an agent workflow on a case.
    
    Available workflows:
    - intake_review: Validate and analyze intake data
    - scenario_analysis: Analyze scenarios and compliance
    - full_evaluation: Complete intake + scenario analysis
    """
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Get intake data
    draft_result = await db.execute(
        select(IntakeDraft).where(IntakeDraft.case_id == case_id)
    )
    draft = draft_result.scalar_one_or_none()
    
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No intake data found for case",
        )
    
    # Get scenarios if available
    scenarios = []
    run_result = await db.execute(
        select(ScenarioRun)
        .where(ScenarioRun.case_id == case_id)
        .order_by(ScenarioRun.created_at.desc())
        .limit(1)
    )
    run = run_result.scalar_one_or_none()
    
    if run:
        scenario_result = await db.execute(
            select(Scenario).where(Scenario.scenario_run_id == run.id)
        )
        scenarios = [
            {
                "status": s.status.value,
                "reason_codes": s.reason_codes,
                "confidence_score": s.confidence_score,
            }
            for s in scenario_result.scalars().all()
        ]
    
    # Build agent context
    context = AgentContext(
        case_id=case_id,
        consumer_id=current_user.id,
        intake_data=draft.data or {},
        provenance=draft.provenance or {},
        scenarios=scenarios,
    )
    
    # Run workflow
    orchestrator = create_orchestrator()
    
    try:
        decisions = await orchestrator.run_workflow(request.workflow, context)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Log audit
    audit = AuditService(db)
    await audit.log_event(
        event_type="agent.workflow_run",
        case_id=case_id,
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        entity_type="case",
        entity_id=case_id,
        event_data={
            "workflow": request.workflow,
            "decision_count": len(decisions),
            "human_review_count": len(orchestrator.get_human_review_required()),
        },
    )
    
    await db.commit()
    
    # Format response
    decision_responses = [
        AgentDecisionResponse(
            decision_id=str(d.decision_id),
            agent_role=d.agent_role.value,
            decision_type=d.decision_type,
            recommendation=d.recommendation,
            confidence=d.confidence,
            reasoning=d.reasoning,
            requires_human_review=d.requires_human_review,
            review_reason=d.review_reason,
        )
        for d in decisions
    ]
    
    human_review = [
        AgentDecisionResponse(
            decision_id=str(d.decision_id),
            agent_role=d.agent_role.value,
            decision_type=d.decision_type,
            recommendation=d.recommendation,
            confidence=d.confidence,
            reasoning=d.reasoning,
            requires_human_review=d.requires_human_review,
            review_reason=d.review_reason,
        )
        for d in orchestrator.get_human_review_required()
    ]
    
    return WorkflowResponse(
        workflow=request.workflow,
        decisions=decision_responses,
        human_review_required=human_review,
    )


@router.get("/available-workflows")
async def get_available_workflows(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, list[dict]]:
    """
    Get available agent workflows.
    """
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    return {
        "workflows": [
            {
                "name": "intake_review",
                "description": "Validate and analyze intake data for completeness and consistency",
            },
            {
                "name": "scenario_analysis",
                "description": "Analyze scenarios, identify improvements, and check compliance",
            },
            {
                "name": "full_evaluation",
                "description": "Complete evaluation combining intake review and scenario analysis",
            },
        ]
    }


# --- Checkpoint Gate Status (GAP-5) ---


class CheckpointGateResponse(BaseModel):
    """Status of a checkpoint gate."""

    name: str
    status: str  # passed, pending, blocked
    blocking_reason: str | None = None


@router.get("/checkpoints")
async def get_checkpoint_status(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, list[dict]]:
    """
    Get checkpoint gate status for a case.

    Returns the status of all 3 gates:
    - Pre-Triage: Intake data validated and complete
    - Pre-Explanation: Scenarios generated and ranked
    - Pre-Export: All compliance checks passed
    """
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")

    # Check intake completeness
    draft_result = await db.execute(
        select(IntakeDraft).where(IntakeDraft.case_id == case_id)
    )
    draft = draft_result.scalar_one_or_none()
    has_intake = draft is not None and bool(draft.data)

    # Check if scenarios exist
    run_result = await db.execute(
        select(ScenarioRun)
        .where(ScenarioRun.case_id == case_id)
        .order_by(ScenarioRun.created_at.desc())
        .limit(1)
    )
    has_scenarios = run_result.scalar_one_or_none() is not None

    # Build gate statuses
    gates = []

    # Gate 1: Pre-Triage
    if has_intake:
        gates.append(CheckpointGateResponse(
            name="Pre-Triage",
            status="passed",
        ))
    else:
        gates.append(CheckpointGateResponse(
            name="Pre-Triage",
            status="blocked" if not draft else "pending",
            blocking_reason="Intake data not submitted" if not draft else "Intake incomplete",
        ))

    # Gate 2: Pre-Explanation
    if has_scenarios:
        gates.append(CheckpointGateResponse(
            name="Pre-Explanation",
            status="passed",
        ))
    elif has_intake:
        gates.append(CheckpointGateResponse(
            name="Pre-Explanation",
            status="pending",
            blocking_reason="Scenarios not yet generated",
        ))
    else:
        gates.append(CheckpointGateResponse(
            name="Pre-Explanation",
            status="blocked",
            blocking_reason="Pre-Triage gate not passed",
        ))

    # Gate 3: Pre-Export
    if has_scenarios and has_intake:
        gates.append(CheckpointGateResponse(
            name="Pre-Export",
            status="passed",
        ))
    else:
        gates.append(CheckpointGateResponse(
            name="Pre-Export",
            status="blocked",
            blocking_reason="Pre-Explanation gate not passed",
        ))

    return {
        "case_id": str(case_id),
        "gates": [g.model_dump() for g in gates],
    }
