"""
GOATCRD Scenarios API Routes
Scenario generation, ranking, and counterfactual simulation

[HARDENING] Task 1.1, 1.2, 1.3: Wired to real services
"""
from datetime import datetime, timezone
from uuid import UUID
import logging

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.models import Case, IntakeSnapshot, Scenario, ScenarioRun, EligibilityStatus
from app.schemas import (
    CounterfactualRequest,
    CounterfactualResponse,
    RankingRequest,
    RankingResponse,
    ScenarioListResponse,
    ScenarioResponse,
    ScenarioRunCreate,
    ScenarioRunResponse,
)
from app.services import AuditService, ScenarioService
from app.engines import CounterfactualSimulator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cases/{case_id}/scenarios", tags=["scenarios"])


@router.post("/run", response_model=ScenarioRunResponse, status_code=status.HTTP_201_CREATED)
async def run_scenarios(
    case_id: UUID,
    run_request: ScenarioRunCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Trigger scenario generation for a case. [HARDENING: R06 - Wired to ScenarioService]"""
    logger.info(f"Running scenarios for case {case_id} by user {current_user.id}")
    
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Verify snapshot exists
    result = await db.execute(
        select(IntakeSnapshot).where(IntakeSnapshot.id == run_request.intake_snapshot_id)
    )
    snapshot = result.scalar_one_or_none()
    if not snapshot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Intake snapshot not found")
    
    # Use ScenarioService to generate scenarios
    scenario_service = ScenarioService(db)
    
    try:
        scenario_run = await scenario_service.run_scenarios(
            case_id=case_id,
            intake_snapshot_id=run_request.intake_snapshot_id,
            actor_id=current_user.id,
            actor_role=current_user.role.value,
        )
        
        logger.info(f"Generated {scenario_run.total_scenarios} scenarios for case {case_id}")
        
        return {
            "id": scenario_run.id,
            "case_id": scenario_run.case_id,
            "intake_snapshot_id": scenario_run.intake_snapshot_id,
            "total_scenarios": scenario_run.total_scenarios,
            "eligible_count": scenario_run.eligible_count,
            "refer_count": scenario_run.refer_count,
            "not_eligible_count": scenario_run.not_eligible_count,
            "program_versions": scenario_run.program_versions,
            "ruleset_versions": scenario_run.ruleset_versions,
            "started_at": scenario_run.started_at,
            "completed_at": scenario_run.completed_at,
            "created_at": scenario_run.created_at,
            "updated_at": scenario_run.updated_at,
        }
    except Exception as e:
        logger.error(f"Scenario generation failed for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Scenario generation failed: {str(e)}"
        )


@router.get("/runs", response_model=list[ScenarioRunResponse])
async def list_scenario_runs(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(default=10, le=50),
) -> list[ScenarioRun]:
    """List scenario runs for a case."""
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    result = await db.execute(
        select(ScenarioRun)
        .where(ScenarioRun.case_id == case_id)
        .order_by(ScenarioRun.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


@router.get("/runs/{run_id}", response_model=ScenarioListResponse)
async def get_scenario_run(
    case_id: UUID,
    run_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get scenario run with all scenarios grouped by status."""
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Get run
    result = await db.execute(
        select(ScenarioRun).where(ScenarioRun.id == run_id, ScenarioRun.case_id == case_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario run not found")
    
    # Get scenarios
    result = await db.execute(
        select(Scenario).where(Scenario.scenario_run_id == run_id)
    )
    scenarios = list(result.scalars().all())
    
    # Group by status
    eligible = [s for s in scenarios if s.status == EligibilityStatus.ELIGIBLE]
    refer = [s for s in scenarios if s.status == EligibilityStatus.REFER]
    not_eligible = [s for s in scenarios if s.status == EligibilityStatus.NOT_ELIGIBLE]
    
    return {
        "scenario_run_id": run_id,
        "total": len(scenarios),
        "eligible": eligible,
        "refer": refer,
        "not_eligible": not_eligible,
    }


@router.post("/runs/{run_id}/rankings", response_model=RankingResponse)
async def get_rankings(
    case_id: UUID,
    run_id: UUID,
    ranking_request: RankingRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get ranked scenarios in a specific mode. [HARDENING: R07 - Wired to ScenarioService]"""
    logger.info(f"Getting rankings for run {run_id} in mode {ranking_request.mode}")
    
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Get run
    result = await db.execute(
        select(ScenarioRun).where(ScenarioRun.id == run_id, ScenarioRun.case_id == case_id)
    )
    run = result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario run not found")
    
    # Use ScenarioService for rankings
    scenario_service = ScenarioService(db)
    
    try:
        ranking_result = await scenario_service.get_rankings(
            scenario_run_id=run_id,
            mode=ranking_request.mode,
        )
        
        return {
            "id": ranking_result.get("id"),
            "scenario_run_id": run_id,
            "mode": ranking_request.mode,
            "ranked_scenarios": ranking_result.get("ranked_scenarios", []),
            "gated_scenarios": ranking_result.get("gated_scenarios", []),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    except Exception as e:
        logger.error(f"Ranking failed for run {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ranking failed: {str(e)}"
        )


@router.post("/simulate", response_model=CounterfactualResponse)
async def simulate_counterfactual(
    case_id: UUID,
    simulation: CounterfactualRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Run a What-If simulation with hypothetical changes. [HARDENING: R18 - Wired to CounterfactualSimulator]"""
    logger.info(f"Running counterfactual simulation for case {case_id}")
    
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Get latest intake snapshot for baseline
    result = await db.execute(
        select(IntakeSnapshot)
        .where(IntakeSnapshot.case_id == case_id)
        .order_by(IntakeSnapshot.created_at.desc())
        .limit(1)
    )
    snapshot = result.scalar_one_or_none()
    
    if not snapshot:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No intake snapshot found for case"
        )
    
    # Use CounterfactualSimulator
    simulator = CounterfactualSimulator()
    
    try:
        # Get baseline scenarios from latest run
        result = await db.execute(
            select(ScenarioRun)
            .where(ScenarioRun.case_id == case_id)
            .order_by(ScenarioRun.created_at.desc())
            .limit(1)
        )
        latest_run = result.scalar_one_or_none()
        
        baseline_scenarios = []
        if latest_run:
            result = await db.execute(
                select(Scenario).where(Scenario.scenario_run_id == latest_run.id)
            )
            baseline_scenarios = [
                {
                    "id": str(s.id),
                    "program_name": s.program_name,
                    "status": s.status.value,
                    "confidence_score": s.confidence_score,
                    "pricing": s.pricing,
                    "reason_codes": s.reason_codes,
                }
                for s in result.scalars().all()
            ]
        
        # Run simulation
        sim_result = simulator.simulate(
            baseline_data=snapshot.normalized_data or snapshot.raw_data,
            hypothetical_changes=simulation.hypothetical_changes,
            baseline_scenarios=baseline_scenarios,
        )
        
        return {
            "case_id": case_id,
            "hypothetical_changes": simulation.hypothetical_changes,
            "status_changes": sim_result.status_changes,
            "changes_summary": sim_result.summary,
            "confidence": sim_result.confidence,
            "confidence_reason": sim_result.confidence_reason,
            "disclaimer": "This is an estimate based on hypothetical changes. Actual eligibility may vary.",
        }
    except Exception as e:
        logger.error(f"Counterfactual simulation failed for case {case_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Simulation failed: {str(e)}"
        )
