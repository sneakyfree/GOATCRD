"""
GOATCRD Retention API Routes
Admin endpoints for data lifecycle management
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession
from app.core.retention import DataType, RetentionPolicy, DEFAULT_RETENTION_POLICIES
from app.models import UserRole

router = APIRouter(prefix="/admin/retention", tags=["admin", "retention"])


class RetentionPolicyResponse(BaseModel):
    """Response for retention policy listing."""
    data_type: str
    retention_days: int
    description: str


class PurgePreviewResponse(BaseModel):
    """Response for purge preview."""
    data_type: str
    retention_days: int
    cutoff_date: str
    records_to_purge: int


class PurgeResultResponse(BaseModel):
    """Response for purge operation."""
    success: bool
    results: dict[str, int]
    total_purged: int


class PurgeRequest(BaseModel):
    """Request to trigger purge."""
    data_type: str | None = None  # None = all types
    confirm: bool = False


def require_admin(current_user: CurrentUser) -> None:
    """Dependency to require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


@router.get("/policies", response_model=list[RetentionPolicyResponse])
async def list_retention_policies(
    current_user: CurrentUser,
) -> list[dict]:
    """List all retention policies."""
    require_admin(current_user)
    
    descriptions = {
        DataType.AUDIT_EVENTS: "Audit trail events for compliance",
        DataType.SESSION_DATA: "User session information",
        DataType.INTAKE_DRAFTS: "Draft intake data before submission",
        DataType.EXPORTS: "Generated export files",
        DataType.PULSE_ALERTS: "Credit pulse monitoring alerts",
        DataType.ACCESS_LOGS: "Data access logs for 1033 compliance",
        DataType.AGENT_ACTIONS: "AI agent action history",
    }
    
    return [
        {
            "data_type": dt.value,
            "retention_days": days,
            "description": descriptions.get(dt, ""),
        }
        for dt, days in DEFAULT_RETENTION_POLICIES.items()
    ]


@router.get("/preview", response_model=list[PurgePreviewResponse])
async def preview_purge(
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    """Preview what data would be purged for each type."""
    require_admin(current_user)
    
    policy = RetentionPolicy(db)
    preview = await policy.get_purge_preview()
    
    return [
        {
            "data_type": dt,
            "retention_days": info["retention_days"],
            "cutoff_date": info["cutoff_date"],
            "records_to_purge": info["records_to_purge"],
        }
        for dt, info in preview.items()
    ]


@router.post("/purge", response_model=PurgeResultResponse)
async def trigger_purge(
    request: PurgeRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """
    Trigger manual data purge.
    
    Requires explicit confirmation to prevent accidental deletion.
    """
    require_admin(current_user)
    
    if not request.confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must set confirm=true to execute purge",
        )
    
    policy = RetentionPolicy(db)
    
    if request.data_type:
        # Purge specific type
        try:
            data_type = DataType(request.data_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data type: {request.data_type}",
            )
        
        count = await policy.purge_expired_data(data_type)
        results = {data_type.value: count}
    else:
        # Purge all types
        results = await policy.purge_all_expired()
    
    await db.commit()
    
    total = sum(v for v in results.values() if v > 0)
    
    return {
        "success": True,
        "results": results,
        "total_purged": total,
    }
