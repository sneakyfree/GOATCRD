"""
GOATCRD Pydantic Schemas - Case and Intake
"""
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, IDSchema, ProvenanceRecord, TimestampSchema


class CaseCreate(BaseSchema):
    """Case creation schema."""
    
    case_type: str | None = None


class CaseResponse(IDSchema, TimestampSchema):
    """Case response schema."""
    
    consumer_id: UUID
    partner_id: UUID | None = None
    status: str
    case_type: str | None = None


class InviteCreate(BaseSchema):
    """Invite creation schema."""
    
    send_to_email: str | None = None
    send_to_phone: str | None = None
    expires_in_hours: int = Field(default=72, ge=1, le=720)


class InviteResponse(IDSchema, TimestampSchema):
    """Invite response schema."""
    
    case_id: UUID
    expires_at: datetime
    used_at: datetime | None = None
    # Token is returned only on creation
    token: str | None = None


# Intake schemas
class IntakeChapter(BaseSchema):
    """Intake chapter definition."""
    
    chapter_id: int
    name: str
    description: str
    fields: list[dict]
    required_for: list[str] = Field(default_factory=list)


class IntakeSchema(BaseSchema):
    """Complete intake schema definition."""
    
    version: str
    chapters: list[IntakeChapter]


class IntakeDraftUpdate(BaseSchema):
    """Intake draft update schema."""
    
    data: dict[str, Any]
    current_chapter: int | None = None


class IntakeDraftResponse(IDSchema, TimestampSchema):
    """Intake draft response."""
    
    case_id: UUID
    data: dict[str, Any]
    current_chapter: int
    completed_chapters: list[int]
    contradictions: list[dict]
    missing_fields: list[str]


class IntakeSnapshotResponse(IDSchema, TimestampSchema):
    """Intake snapshot response."""
    
    case_id: UUID
    version: int
    provenance: dict[str, ProvenanceRecord]
    contradictions_resolved: bool


class IntakeSubmit(BaseSchema):
    """Intake submission for snapshot creation."""
    
    confirm_review: bool = Field(
        ..., 
        description="Consumer confirms they have reviewed and verified the information"
    )
