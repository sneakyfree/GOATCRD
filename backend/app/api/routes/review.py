"""
GOATCRD Human Review Queue API Routes
Ticket management for REFER cases and human oversight
"""
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentUser, DBSession
from app.models import (
    Case,
    ReviewTicket,
    Override,
    UserRole,
    Scenario,
)
from app.services import AuditService

router = APIRouter(prefix="/review", tags=["review"])


# --- Request/Response Schemas ---

class TicketSummary(BaseModel):
    """Summary of a review ticket."""
    id: UUID
    case_id: UUID
    trigger_reason: str
    status: str
    priority: str
    assigned_to: UUID | None
    created_at: datetime
    consumer_name: str | None = None
    scenario_count: int = 0


class TicketDetail(BaseModel):
    """Full ticket details with case context."""
    id: UUID
    case_id: UUID
    trigger_reason: str
    status: str
    priority: str
    assigned_to: UUID | None
    created_at: datetime
    resolved_at: datetime | None
    resolution_notes: str | None
    case_type: str | None
    intake_summary: dict | None
    scenarios: list[dict]
    overrides: list[dict]


class AssignRequest(BaseModel):
    """Request to assign ticket to reviewer."""
    reviewer_id: UUID


class ResolveRequest(BaseModel):
    """Request to resolve a ticket."""
    resolution_notes: str = Field(..., min_length=10)
    status: Literal["approved", "declined", "escalated"] = "approved"


class OverrideRequest(BaseModel):
    """Request to override a scenario outcome."""
    scenario_id: UUID
    new_status: Literal["eligible", "refer", "not_eligible"]
    reason: str = Field(..., min_length=10)
    evidence_notes: str | None = None


class QueueStats(BaseModel):
    """Queue statistics."""
    pending: int
    in_review: int
    resolved_today: int
    avg_resolution_hours: float


# --- Helper ---

def require_reviewer(current_user: CurrentUser) -> None:
    """Require reviewer or admin role."""
    if current_user.role not in (UserRole.ADMIN, UserRole.REVIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Reviewer role required",
        )


# --- Endpoints ---

@router.get("/queue", response_model=list[TicketSummary])
async def list_queue(
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = None,
    assigned_to_me: bool = False,
    priority: str | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[dict]:
    """List pending review tickets."""
    require_reviewer(current_user)
    
    query = select(ReviewTicket).options(
        selectinload(ReviewTicket.case)
    )
    
    if status_filter:
        query = query.where(ReviewTicket.status == status_filter)
    else:
        # Default: pending and in_review
        query = query.where(ReviewTicket.status.in_(["pending", "in_review"]))
    
    if assigned_to_me:
        query = query.where(ReviewTicket.assigned_to == current_user.id)
    
    if priority:
        query = query.where(ReviewTicket.priority == priority)
    
    query = query.order_by(
        ReviewTicket.priority.desc(),
        ReviewTicket.created_at.asc(),
    ).limit(limit).offset(offset)
    
    result = await db.execute(query)
    tickets = list(result.scalars().all())
    
    summaries = []
    for ticket in tickets:
        # Get scenario count
        scenario_result = await db.execute(
            select(func.count(Scenario.id)).where(
                Scenario.case_id == ticket.case_id
            )
        )
        scenario_count = scenario_result.scalar() or 0
        
        summaries.append({
            "id": ticket.id,
            "case_id": ticket.case_id,
            "trigger_reason": ticket.trigger_reason,
            "status": ticket.status,
            "priority": ticket.priority,
            "assigned_to": ticket.assigned_to,
            "created_at": ticket.created_at,
            "consumer_name": None,  # Would get from case
            "scenario_count": scenario_count,
        })
    
    return summaries


@router.get("/stats", response_model=QueueStats)
async def get_queue_stats(
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get queue statistics."""
    require_reviewer(current_user)
    
    # Pending count
    pending_result = await db.execute(
        select(func.count(ReviewTicket.id)).where(
            ReviewTicket.status == "pending"
        )
    )
    pending = pending_result.scalar() or 0
    
    # In review count
    in_review_result = await db.execute(
        select(func.count(ReviewTicket.id)).where(
            ReviewTicket.status == "in_review"
        )
    )
    in_review = in_review_result.scalar() or 0
    
    # Resolved today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today_result = await db.execute(
        select(func.count(ReviewTicket.id)).where(
            ReviewTicket.status == "resolved",
            ReviewTicket.resolved_at >= today_start,
        )
    )
    resolved_today = resolved_today_result.scalar() or 0
    
    return {
        "pending": pending,
        "in_review": in_review,
        "resolved_today": resolved_today,
        "avg_resolution_hours": 4.2,  # Would calculate from actual data
    }


@router.get("/tickets/{ticket_id}", response_model=TicketDetail)
async def get_ticket(
    ticket_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Get full ticket details with case context."""
    require_reviewer(current_user)
    
    result = await db.execute(
        select(ReviewTicket).options(
            selectinload(ReviewTicket.case),
            selectinload(ReviewTicket.overrides),
        ).where(ReviewTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Get scenarios for case
    scenario_result = await db.execute(
        select(Scenario).where(Scenario.case_id == ticket.case_id)
    )
    scenarios = list(scenario_result.scalars().all())
    
    return {
        "id": ticket.id,
        "case_id": ticket.case_id,
        "trigger_reason": ticket.trigger_reason,
        "status": ticket.status,
        "priority": ticket.priority,
        "assigned_to": ticket.assigned_to,
        "created_at": ticket.created_at,
        "resolved_at": ticket.resolved_at,
        "resolution_notes": ticket.resolution_notes,
        "case_type": ticket.case.case_type.value if ticket.case else None,
        "intake_summary": {},  # Would get from intake snapshot
        "scenarios": [
            {
                "id": str(s.id),
                "program_name": s.program_name,
                "status": s.status.value,
                "confidence_score": s.confidence_score,
                "reason_codes": s.reason_codes or [],
            }
            for s in scenarios
        ],
        "overrides": [
            {
                "id": str(o.id),
                "scenario_id": str(o.scenario_id) if hasattr(o, 'scenario_id') else None,
                "reason": o.reason,
                "created_at": o.created_at,
            }
            for o in (ticket.overrides or [])
        ],
    }


@router.post("/tickets/{ticket_id}/assign")
async def assign_ticket(
    ticket_id: UUID,
    request: AssignRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Assign ticket to a reviewer."""
    require_reviewer(current_user)
    
    result = await db.execute(
        select(ReviewTicket).where(ReviewTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    ticket.assigned_to = request.reviewer_id
    ticket.status = "in_review"
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="ticket_assigned",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={
            "ticket_id": str(ticket.id),
            "assigned_to": str(request.reviewer_id),
        },
    )
    
    await db.flush()
    
    return {"success": True, "message": "Ticket assigned"}


@router.post("/tickets/{ticket_id}/resolve")
async def resolve_ticket(
    ticket_id: UUID,
    request: ResolveRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Resolve a review ticket."""
    require_reviewer(current_user)
    
    result = await db.execute(
        select(ReviewTicket).where(ReviewTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    if ticket.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket already resolved",
        )
    
    ticket.status = "resolved"
    ticket.resolved_at = datetime.now(timezone.utc)
    ticket.resolution_notes = request.resolution_notes
    ticket.resolved_by = current_user.id
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="ticket_resolved",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={
            "ticket_id": str(ticket.id),
            "resolution": request.status,
        },
    )
    
    await db.flush()
    
    return {"success": True, "message": "Ticket resolved"}


@router.post("/tickets/{ticket_id}/override")
async def create_override(
    ticket_id: UUID,
    request: OverrideRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Override a scenario outcome with justification."""
    require_reviewer(current_user)
    
    result = await db.execute(
        select(ReviewTicket).where(ReviewTicket.id == ticket_id)
    )
    ticket = result.scalar_one_or_none()
    
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    
    # Verify scenario exists
    scenario_result = await db.execute(
        select(Scenario).where(Scenario.id == request.scenario_id)
    )
    scenario = scenario_result.scalar_one_or_none()
    
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )
    
    # Create override record
    override = Override(
        ticket_id=ticket.id,
        scenario_id=request.scenario_id,
        original_status=scenario.status.value,
        new_status=request.new_status,
        reason=request.reason,
        evidence_notes=request.evidence_notes,
        created_by=current_user.id,
    )
    
    db.add(override)
    
    # TODO: Update scenario status and create new snapshot version
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="scenario_override",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={
            "ticket_id": str(ticket.id),
            "scenario_id": str(request.scenario_id),
            "original_status": scenario.status.value,
            "new_status": request.new_status,
            "reason": request.reason,
        },
    )
    
    await db.flush()
    
    return {"success": True, "message": "Override created", "override_id": str(override.id)}
