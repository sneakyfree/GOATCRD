"""
GOATCRD Cases API Routes
Case management and intake
"""
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession
from app.core.security import get_password_hash
from app.models import Case, CaseStatus, IntakeDraft, IntakeSnapshot, Invite, User
from app.schemas import (
    CaseCreate,
    CaseResponse,
    IntakeDraftResponse,
    IntakeDraftUpdate,
    IntakeSnapshotResponse,
    IntakeSubmit,
    InviteCreate,
    InviteResponse,
)
from app.services import AuditService
from app.services.intake import IntakeService

router = APIRouter(prefix="/cases", tags=["cases"])


@router.post("", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: CaseCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> Case:
    """Create a new case for the current user."""
    case = Case(
        consumer_id=current_user.id,
        case_type=case_in.case_type,
        status=CaseStatus.DRAFT,
    )
    
    db.add(case)
    await db.flush()
    
    # Log audit event
    audit = AuditService(db)
    await audit.log_case_created(
        case_id=case.id,
        actor_id=current_user.id,
        actor_role=current_user.role.value,
    )
    
    await db.refresh(case)
    return case


@router.get("", response_model=list[CaseResponse])
async def list_cases(
    current_user: CurrentUser,
    db: DBSession,
    status_filter: CaseStatus | None = Query(None),
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Case]:
    """List cases for the current user."""
    query = select(Case).where(Case.consumer_id == current_user.id)
    
    if status_filter:
        query = query.where(Case.status == status_filter)
    
    query = query.order_by(Case.created_at.desc()).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> Case:
    """Get a specific case."""
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    return case


@router.post("/{case_id}/invites", response_model=InviteResponse, status_code=status.HTTP_201_CREATED)
async def create_invite(
    case_id: UUID,
    invite_in: InviteCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Create a secure invite link for mobile-first intake."""
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    invite = Invite(
        case_id=case_id,
        token_hash=get_password_hash(token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=invite_in.expires_in_hours),
        sent_to_email=invite_in.send_to_email,
        sent_to_phone=invite_in.send_to_phone,
    )
    
    db.add(invite)
    await db.flush()
    await db.refresh(invite)
    
    # Send invite via email/SMS (feature-flag gated)
    from app.services.notifications import NotificationService
    notification_service = NotificationService()
    await notification_service.send_invite(
        token=token,
        expires_at=invite.expires_at,
        email=invite_in.send_to_email,
        phone=invite_in.send_to_phone,
        expires_hours=invite_in.expires_in_hours,
    )
    
    # Return invite with token (only shown once)
    return {
        "id": invite.id,
        "case_id": invite.case_id,
        "expires_at": invite.expires_at,
        "used_at": invite.used_at,
        "token": token,  # Only returned on creation
        "created_at": invite.created_at,
        "updated_at": invite.updated_at,
    }


# Intake draft routes
@router.get("/{case_id}/intake/draft", response_model=IntakeDraftResponse)
async def get_intake_draft(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> IntakeDraft:
    """Get the current intake draft for a case."""
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Get or create draft
    result = await db.execute(
        select(IntakeDraft).where(IntakeDraft.case_id == case_id).order_by(IntakeDraft.updated_at.desc())
    )
    draft = result.scalar_one_or_none()
    
    if not draft:
        draft = IntakeDraft(case_id=case_id, data={}, current_chapter=1)
        db.add(draft)
        await db.flush()
        await db.refresh(draft)
    
    return draft


@router.put("/{case_id}/intake/draft", response_model=IntakeDraftResponse)
async def update_intake_draft(
    case_id: UUID,
    draft_update: IntakeDraftUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> IntakeDraft:
    """Update the intake draft (save progress) with provenance tracking."""
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Delegate to IntakeService — handles provenance tracking per field
    intake_service = IntakeService(db)
    draft = await intake_service.update_draft(
        case_id=case_id,
        field_updates=draft_update.data,
        current_chapter=draft_update.current_chapter,
    )
    
    return draft


@router.post("/{case_id}/intake/submit", response_model=IntakeSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def submit_intake(
    case_id: UUID,
    submit: IntakeSubmit,
    current_user: CurrentUser,
    db: DBSession,
) -> IntakeSnapshot:
    """Submit intake and create immutable snapshot with normalization and provenance."""
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Delegate to IntakeService — handles normalization, provenance, contradiction checks
    intake_service = IntakeService(db)
    try:
        snapshot = await intake_service.submit_intake(
            case_id=case_id,
            actor_id=current_user.id,
            confirm_review=submit.confirm_review,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    return snapshot
