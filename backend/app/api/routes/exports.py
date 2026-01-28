"""
GOATCRD Exports API Routes
Export generation for scenarios and consumer data
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.engines.export import export_engine
from app.models import Case, Scenario, ScenarioRun
from app.schemas import SuccessResponse
from app.services import AuditService

router = APIRouter(prefix="/cases/{case_id}/exports", tags=["exports"])


@router.post("/scenarios")
async def export_scenarios(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
    format: str = Query(default="json", pattern="^(json|pdf|csv)$"),
    run_id: UUID | None = Query(default=None),
):
    """
    Export scenarios for a case.
    
    Supports JSON, PDF (HTML template), and CSV formats.
    """
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Get scenario run
    if run_id:
        run_result = await db.execute(
            select(ScenarioRun).where(
                ScenarioRun.id == run_id,
                ScenarioRun.case_id == case_id,
            )
        )
    else:
        # Get latest run
        run_result = await db.execute(
            select(ScenarioRun)
            .where(ScenarioRun.case_id == case_id)
            .order_by(ScenarioRun.created_at.desc())
            .limit(1)
        )
    
    run = run_result.scalar_one_or_none()
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No scenario run found for this case",
        )
    
    # Get scenarios
    scenarios_result = await db.execute(
        select(Scenario).where(Scenario.scenario_run_id == run.id)
    )
    scenarios = list(scenarios_result.scalars().all())
    
    # Convert to dicts
    scenario_dicts = [
        {
            "program_name": "Program",  # Would join with programs table
            "status": s.status.value,
            "confidence_score": s.confidence_score,
            "pricing": s.pricing,
            "reason_codes": s.reason_codes,
            "verify_checklist": s.verify_checklist,
        }
        for s in scenarios
    ]
    
    # Generate export
    export = export_engine.export_scenario_summary(
        case_id=case_id,
        scenarios=scenario_dicts,
        rankings=None,
        format=format,
    )
    
    # Log audit
    audit = AuditService(db)
    await audit.log_export_generated(
        case_id=case_id,
        export_id=run.id,  # Using run ID as export reference
        export_type="scenario_summary",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
    )
    
    await db.commit()
    
    # Return based on format
    if format == "json":
        return JSONResponse(
            content={
                "filename": export.filename,
                "content": export.content if isinstance(export.content, dict) else None,
                "metadata": export.metadata,
            }
        )
    elif format == "csv":
        return PlainTextResponse(
            content=export.content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{export.filename}"'},
        )
    else:
        # PDF returns HTML template
        return PlainTextResponse(
            content=export.content,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{export.filename}"'},
        )
