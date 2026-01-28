"""
GOATCRD Consent API Routes
1033-Native consent management
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.models import AccessLog, Case, Consent, ConsentEvent, ConsentScope, ConsentStatus
from app.schemas import (
    AccessLogEntry,
    ConsentEventResponse,
    ConsentGrant,
    ConsentRequest,
    ConsentResponse,
    ConsentRevoke,
    DataExportRequest,
    SuccessResponse,
)
from app.services import AuditService

router = APIRouter(prefix="/consents", tags=["consents"])


@router.post("", response_model=ConsentResponse, status_code=status.HTTP_201_CREATED)
async def request_consent(
    consent_in: ConsentRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> Consent:
    """Request consent for a specific data scope."""
    # Validate scope
    try:
        scope = ConsentScope(consent_in.scope)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid consent scope: {consent_in.scope}",
        )
    
    # Create consent request
    consent = Consent(
        consumer_id=current_user.id,
        scope=scope,
        provider=consent_in.provider,
        purpose=consent_in.purpose,
        status=ConsentStatus.REQUESTED,
        requested_at=datetime.now(timezone.utc),
        expires_at=(
            datetime.now(timezone.utc) + timedelta(days=consent_in.expires_in_days)
            if consent_in.expires_in_days
            else None
        ),
    )
    
    db.add(consent)
    await db.flush()
    
    # Log consent event
    event = ConsentEvent(
        consent_id=consent.id,
        event_type="requested",
        actor_id=current_user.id,
    )
    db.add(event)
    
    await db.refresh(consent)
    return consent


@router.post("/{consent_id}/grant", response_model=ConsentResponse)
async def grant_consent(
    consent_id: UUID,
    grant: ConsentGrant,
    current_user: CurrentUser,
    db: DBSession,
) -> Consent:
    """Grant a consent request."""
    if not grant.acknowledge_terms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must acknowledge the terms to grant consent",
        )
    
    # Get consent
    result = await db.execute(
        select(Consent).where(
            Consent.id == consent_id,
            Consent.consumer_id == current_user.id,
        )
    )
    consent = result.scalar_one_or_none()
    
    if not consent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent not found")
    
    if consent.status != ConsentStatus.REQUESTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Consent is already {consent.status.value}",
        )
    
    # Grant consent
    consent.status = ConsentStatus.GRANTED
    consent.granted_at = datetime.now(timezone.utc)
    
    # Log event
    event = ConsentEvent(
        consent_id=consent.id,
        event_type="granted",
        actor_id=current_user.id,
    )
    db.add(event)
    
    # Audit log
    audit = AuditService(db)
    await audit.log_consent_granted(
        consent_id=consent.id,
        scope=consent.scope.value,
        actor_id=current_user.id,
    )
    
    await db.refresh(consent)
    return consent


@router.post("/{consent_id}/revoke", response_model=ConsentResponse)
async def revoke_consent(
    consent_id: UUID,
    revoke: ConsentRevoke,
    current_user: CurrentUser,
    db: DBSession,
) -> Consent:
    """Revoke a granted consent."""
    # Get consent
    result = await db.execute(
        select(Consent).where(
            Consent.id == consent_id,
            Consent.consumer_id == current_user.id,
        )
    )
    consent = result.scalar_one_or_none()
    
    if not consent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent not found")
    
    if consent.status not in (ConsentStatus.GRANTED, ConsentStatus.REQUESTED):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot revoke consent in status: {consent.status.value}",
        )
    
    # Revoke consent
    consent.status = ConsentStatus.REVOKED
    consent.revoked_at = datetime.now(timezone.utc)
    
    # Log event
    event = ConsentEvent(
        consent_id=consent.id,
        event_type="revoked",
        actor_id=current_user.id,
        event_data={"reason": revoke.reason} if revoke.reason else None,
    )
    db.add(event)
    
    # Audit log
    audit = AuditService(db)
    await audit.log_consent_revoked(
        consent_id=consent.id,
        scope=consent.scope.value,
        actor_id=current_user.id,
    )
    
    # TODO: Trigger downstream disablement verification
    
    await db.refresh(consent)
    return consent


@router.get("", response_model=list[ConsentResponse])
async def list_consents(
    current_user: CurrentUser,
    db: DBSession,
    status_filter: str | None = Query(None),
) -> list[Consent]:
    """List all consents for current user."""
    query = select(Consent).where(Consent.consumer_id == current_user.id)
    
    if status_filter:
        query = query.where(Consent.status == ConsentStatus(status_filter))
    
    query = query.order_by(Consent.created_at.desc())
    
    result = await db.execute(query)
    return list(result.scalars().all())


# 1033 Consumer Rights endpoints
@router.get("/access-log", response_model=list[AccessLogEntry])
async def get_access_log(
    current_user: CurrentUser,
    db: DBSession,
    limit: int = Query(default=100, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AccessLog]:
    """Get access log for current user (1033 compliance)."""
    query = (
        select(AccessLog)
        .where(AccessLog.consumer_id == current_user.id)
        .order_by(AccessLog.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/data-export", response_model=SuccessResponse)
async def request_data_export(
    export_request: DataExportRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> SuccessResponse:
    """Request a data export (1033 compliance)."""
    # TODO: Implement async export job
    # This would trigger a background task to compile all consumer data
    
    return SuccessResponse(
        success=True,
        message=f"Data export request submitted. You will receive your data in {export_request.format} format.",
    )
