"""
GOATCRD Pulse API Routes
Credit monitoring subscriptions and alerts
"""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from app.api.deps import CurrentUser, DBSession
from app.models.pulse import (
    PulseAlert,
    PulseEventType,
    PulseFrequency,
    PulseSubscription,
)
from app.services import AuditService

router = APIRouter(prefix="/pulse", tags=["pulse"])


# --- Request/Response Schemas ---

class SubscribeRequest(BaseModel):
    """Request to subscribe to pulse monitoring."""
    frequency: PulseFrequency = PulseFrequency.DAILY
    event_types: list[str] = Field(default_factory=list)  # Empty = all events
    consent_id: UUID | None = None


class SubscriptionResponse(BaseModel):
    """Subscription response."""
    id: UUID
    frequency: str
    event_types: list[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Alert response."""
    id: UUID
    event_type: str
    detected_at: datetime
    summary: str
    impact: str | None
    suggested_action: str | None
    scenario_refresh_available: bool
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertsListResponse(BaseModel):
    """List of alerts with metadata."""
    alerts: list[AlertResponse]
    total: int
    unread_count: int


# --- Endpoints ---

@router.post("/subscribe", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_pulse(
    request: SubscribeRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PulseSubscription:
    """Opt-in to credit pulse monitoring."""
    # Check for existing active subscription
    result = await db.execute(
        select(PulseSubscription).where(
            PulseSubscription.consumer_id == current_user.id,
            PulseSubscription.is_active == True,
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Active subscription already exists. Use PUT to update.",
        )
    
    subscription = PulseSubscription(
        consumer_id=current_user.id,
        frequency=request.frequency,
        event_types=request.event_types,
        consent_id=request.consent_id,
        is_active=True,
    )
    
    db.add(subscription)
    await db.flush()
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="pulse_subscribed",
        actor_id=current_user.id,
        event_data={"frequency": request.frequency.value},
    )
    
    await db.refresh(subscription)
    return subscription


@router.get("/subscribe", response_model=SubscriptionResponse | None)
async def get_subscription(
    current_user: CurrentUser,
    db: DBSession,
) -> PulseSubscription | None:
    """Get current pulse subscription."""
    result = await db.execute(
        select(PulseSubscription).where(
            PulseSubscription.consumer_id == current_user.id,
            PulseSubscription.is_active == True,
        )
    )
    return result.scalar_one_or_none()


@router.put("/subscribe", response_model=SubscriptionResponse)
async def update_subscription(
    request: SubscribeRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> PulseSubscription:
    """Update pulse subscription settings."""
    result = await db.execute(
        select(PulseSubscription).where(
            PulseSubscription.consumer_id == current_user.id,
            PulseSubscription.is_active == True,
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    subscription.frequency = request.frequency
    subscription.event_types = request.event_types
    
    await db.flush()
    await db.refresh(subscription)
    return subscription


@router.delete("/subscribe")
async def unsubscribe_from_pulse(
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Opt-out from credit pulse monitoring."""
    result = await db.execute(
        select(PulseSubscription).where(
            PulseSubscription.consumer_id == current_user.id,
            PulseSubscription.is_active == True,
        )
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found",
        )
    
    subscription.is_active = False
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="pulse_unsubscribed",
        actor_id=current_user.id,
    )
    
    await db.flush()
    
    return {"success": True, "message": "Unsubscribed from pulse monitoring"}


@router.get("/alerts", response_model=AlertsListResponse)
async def list_alerts(
    current_user: CurrentUser,
    db: DBSession,
    unread_only: bool = False,
    event_type: PulseEventType | None = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    """List pulse alerts for current user."""
    query = select(PulseAlert).where(
        PulseAlert.consumer_id == current_user.id
    )
    
    if unread_only:
        query = query.where(PulseAlert.is_read == False)
    
    if event_type:
        query = query.where(PulseAlert.event_type == event_type)
    
    # Get total count
    count_query = select(func.count(PulseAlert.id)).where(
        PulseAlert.consumer_id == current_user.id
    )
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get unread count
    unread_query = select(func.count(PulseAlert.id)).where(
        PulseAlert.consumer_id == current_user.id,
        PulseAlert.is_read == False,
    )
    unread_result = await db.execute(unread_query)
    unread_count = unread_result.scalar() or 0
    
    # Get alerts
    query = query.order_by(PulseAlert.detected_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    alerts = list(result.scalars().all())
    
    return {
        "alerts": alerts,
        "total": total,
        "unread_count": unread_count,
    }


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Mark an alert as read."""
    result = await db.execute(
        select(PulseAlert).where(
            PulseAlert.id == alert_id,
            PulseAlert.consumer_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    alert.is_read = True
    alert.read_at = datetime.now(timezone.utc)
    
    await db.flush()
    
    return {"success": True}


@router.post("/alerts/{alert_id}/refresh-scenarios")
async def trigger_scenario_refresh(
    alert_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Trigger scenario refresh based on alert."""
    result = await db.execute(
        select(PulseAlert).where(
            PulseAlert.id == alert_id,
            PulseAlert.consumer_id == current_user.id,
        )
    )
    alert = result.scalar_one_or_none()
    
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    
    if not alert.scenario_refresh_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scenario refresh not available for this alert",
        )
    
    if alert.scenario_refresh_triggered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scenario refresh already triggered",
        )
    
    alert.scenario_refresh_triggered = True
    
    # TODO: Actually trigger scenario regeneration
    # This would queue a background job to re-run scenarios with updated data
    
    await db.flush()
    
    return {"success": True, "message": "Scenario refresh triggered"}


# Case-specific pulse endpoint
cases_pulse_router = APIRouter(tags=["cases", "pulse"])


@cases_pulse_router.get("/cases/{case_id}/pulse", response_model=list[AlertResponse])
async def get_case_pulse_alerts(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(default=20, le=50),
) -> list[PulseAlert]:
    """Get pulse alerts for a specific case."""
    # Verify case ownership (basic check)
    from app.models import Case
    
    case_result = await db.execute(
        select(Case).where(
            Case.id == case_id,
            Case.consumer_id == current_user.id,
        )
    )
    if not case_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    result = await db.execute(
        select(PulseAlert).where(
            PulseAlert.case_id == case_id,
            PulseAlert.consumer_id == current_user.id,
        ).order_by(PulseAlert.detected_at.desc()).limit(limit)
    )
    
    return list(result.scalars().all())
