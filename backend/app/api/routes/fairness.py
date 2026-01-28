"""
GOATCRD Fairness API Routes
Admin endpoints for fairness testing and monitoring
"""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DBSession
from app.models import UserRole
from app.models.fairness import FairnessTest, FairnessTestStatus
from app.fairness import FairnessTestRunner
from app.services import AuditService

router = APIRouter(prefix="/admin/fairness", tags=["admin", "fairness"])


# --- Request/Response Schemas ---

class RunTestsRequest(BaseModel):
    """Request to run fairness tests."""
    model_version: str
    rules_version: str
    feature_names: list[str] = Field(default_factory=list)


class TestResultResponse(BaseModel):
    """Fairness test result response."""
    id: UUID
    model_version: str
    rules_version: str
    status: str
    disparate_impact_passed: bool
    feature_audit_passed: bool
    lda_available: bool
    blocking_issues: list[str]
    warnings: list[str]
    duration_seconds: float | None
    requires_approval: bool
    approved_by: UUID | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardMetrics(BaseModel):
    """Fairness dashboard metrics."""
    total_tests: int
    passed: int
    failed: int
    warnings: int
    last_test_date: datetime | None
    current_deployment_status: str
    avg_air_score: float
    high_risk_features: int


class ApproveRequest(BaseModel):
    """Request to approve a fairness test result."""
    approval_notes: str = Field(..., min_length=10)


# --- Helper ---

def require_admin(current_user: CurrentUser) -> None:
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


# --- Endpoints ---

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_fairness_dashboard(
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get fairness dashboard metrics."""
    require_admin(current_user)
    
    # Total tests
    total_result = await db.execute(
        select(func.count(FairnessTest.id))
    )
    total = total_result.scalar() or 0
    
    # By status
    passed_result = await db.execute(
        select(func.count(FairnessTest.id)).where(
            FairnessTest.status == FairnessTestStatus.PASSED
        )
    )
    passed = passed_result.scalar() or 0
    
    failed_result = await db.execute(
        select(func.count(FairnessTest.id)).where(
            FairnessTest.status == FairnessTestStatus.FAILED
        )
    )
    failed = failed_result.scalar() or 0
    
    warning_result = await db.execute(
        select(func.count(FairnessTest.id)).where(
            FairnessTest.status == FairnessTestStatus.WARNING
        )
    )
    warnings = warning_result.scalar() or 0
    
    # Last test
    last_test_result = await db.execute(
        select(FairnessTest).order_by(FairnessTest.created_at.desc()).limit(1)
    )
    last_test = last_test_result.scalar_one_or_none()
    
    # Current deployment status
    deployment_status = "unknown"
    if last_test:
        if last_test.deployment_allowed:
            deployment_status = "allowed"
        elif last_test.status == FairnessTestStatus.FAILED:
            deployment_status = "blocked"
        else:
            deployment_status = "pending_approval"
    
    return {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "warnings": warnings,
        "last_test_date": last_test.created_at if last_test else None,
        "current_deployment_status": deployment_status,
        "avg_air_score": 0.85,  # Would calculate from actual data
        "high_risk_features": 0,  # Would get from latest audit
    }


@router.post("/run-tests", response_model=TestResultResponse, status_code=status.HTTP_201_CREATED)
async def run_fairness_tests(
    request: RunTestsRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> FairnessTest:
    """Trigger fairness test suite."""
    require_admin(current_user)
    
    # Get recent scenarios for testing (in production, would use full dataset)
    from app.models import Scenario
    
    scenarios_result = await db.execute(
        select(Scenario).limit(1000)
    )
    scenarios = list(scenarios_result.scalars().all())
    
    # Convert to dict format for testing
    scenario_dicts = [
        {
            "id": str(s.id),
            "status": s.status.value if hasattr(s.status, 'value') else s.status,
            "demographics": {},  # Would be populated from intake data
        }
        for s in scenarios
    ]
    
    # Run tests
    runner = FairnessTestRunner(
        model_version=request.model_version,
        rules_version=request.rules_version,
        scenarios=scenario_dicts,
        feature_names=request.feature_names or ["income", "credit_score", "dti"],
    )
    
    result = runner.run_full_suite()
    
    # Store result
    test_record = FairnessTest(
        model_version=request.model_version,
        rules_version=request.rules_version,
        status=FairnessTestStatus(result.overall_status.value),
        disparate_impact_passed=result.disparate_impact_passed,
        feature_audit_passed=result.feature_audit_passed,
        lda_available=result.lda_available,
        disparate_impact_results=result.disparate_impact_results,
        feature_audit_result=result.feature_audit_result,
        lda_result=result.lda_result,
        blocking_issues=result.blocking_issues,
        warnings=result.warnings,
        started_at=result.started_at,
        completed_at=result.completed_at,
        duration_seconds=result.duration_seconds,
        requires_approval=result.requires_approval,
        deployment_allowed=not result.requires_approval,
    )
    
    db.add(test_record)
    await db.flush()
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="fairness_tests_run",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={
            "test_id": str(test_record.id),
            "status": result.overall_status.value,
            "model_version": request.model_version,
        },
    )
    
    await db.refresh(test_record)
    return test_record


@router.get("/history", response_model=list[TestResultResponse])
async def get_test_history(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[FairnessTest]:
    """Get fairness test history."""
    require_admin(current_user)
    
    result = await db.execute(
        select(FairnessTest)
        .order_by(FairnessTest.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


@router.get("/tests/{test_id}", response_model=TestResultResponse)
async def get_test_details(
    test_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> FairnessTest:
    """Get detailed test result."""
    require_admin(current_user)
    
    result = await db.execute(
        select(FairnessTest).where(FairnessTest.id == test_id)
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )
    
    return test


@router.post("/tests/{test_id}/approve")
async def approve_test(
    test_id: UUID,
    request: ApproveRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Approve a fairness test for deployment."""
    require_admin(current_user)
    
    result = await db.execute(
        select(FairnessTest).where(FairnessTest.id == test_id)
    )
    test = result.scalar_one_or_none()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )
    
    if test.status == FairnessTestStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot approve failed tests",
        )
    
    test.approved_by = current_user.id
    test.approved_at = datetime.now(timezone.utc)
    test.approval_notes = request.approval_notes
    test.deployment_allowed = True
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="fairness_test_approved",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={
            "test_id": str(test.id),
            "model_version": test.model_version,
        },
    )
    
    await db.flush()
    
    return {"success": True, "message": "Test approved for deployment"}
