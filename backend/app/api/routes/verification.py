"""
GOATCRD Verification API Routes
Data verification endpoints
"""
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.models import Case
from app.services import IntakeService, verification_service

router = APIRouter(prefix="/cases/{case_id}/verification", tags=["verification"])


class VerifyFieldRequest(BaseModel):
    """Request to verify a field."""
    
    field_name: str
    preferred_method: str | None = None
    context: dict[str, Any] | None = None


class VerifyFieldResponse(BaseModel):
    """Response from field verification."""
    
    success: bool
    field_name: str
    verified_value: Any | None
    source_type: str
    verification_method: str
    confidence: int
    error: str | None = None


class VerifyChecklistItem(BaseModel):
    """Verification checklist item."""
    
    field: str
    action: str
    priority: str
    methods: list[str] | None = None


@router.get("/methods/{field_name}")
async def get_verification_methods(
    case_id: UUID,
    field_name: str,
    current_user: CurrentUser,
    db: DBSession,
) -> dict[str, list[str]]:
    """
    Get available verification methods for a field.
    """
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    methods = verification_service.get_available_methods(field_name)
    
    return {
        "field_name": field_name,
        "available_methods": methods,
    }


@router.post("/verify", response_model=VerifyFieldResponse)
async def verify_field(
    case_id: UUID,
    request: VerifyFieldRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> VerifyFieldResponse:
    """
    Verify a field from an authoritative source.
    """
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    # Get current value from intake
    intake_service = IntakeService(db)
    draft = await intake_service.get_or_create_draft(case_id)
    
    current_value = draft.data.get(request.field_name)
    if current_value is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Field {request.field_name} has no value to verify",
        )
    
    # Verify
    verification_result = await verification_service.verify_field(
        field_name=request.field_name,
        provided_value=current_value,
        preferred_method=request.preferred_method,
        context=request.context,
    )
    
    # Update draft if successful
    if verification_result.success:
        await intake_service.verify_field(
            case_id=case_id,
            field_name=request.field_name,
            verified_value=verification_result.verified_value,
            source_type=verification_result.source_type,
            source_id=verification_result.source_id,
            verification_method=verification_result.verification_method,
        )
        await db.commit()
    
    return VerifyFieldResponse(
        success=verification_result.success,
        field_name=verification_result.field_name,
        verified_value=verification_result.verified_value,
        source_type=verification_result.source_type,
        verification_method=verification_result.verification_method,
        confidence=verification_result.confidence,
        error=verification_result.error,
    )


@router.get("/checklist", response_model=list[VerifyChecklistItem])
async def get_verification_checklist(
    case_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[VerifyChecklistItem]:
    """
    Get verification checklist for a case.
    """
    # Verify case ownership
    result = await db.execute(
        select(Case).where(Case.id == case_id, Case.consumer_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case not found")
    
    intake_service = IntakeService(db)
    checklist = await intake_service.get_verify_checklist(case_id)
    
    # Add available methods to each item
    for item in checklist:
        item["methods"] = verification_service.get_available_methods(item["field"])
    
    return [VerifyChecklistItem(**item) for item in checklist]
