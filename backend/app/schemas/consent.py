"""
GOATCRD Pydantic Schemas - Consent
1033-Native consent schemas
"""
from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, IDSchema, TimestampSchema


class ConsentRequest(BaseSchema):
    """Consent grant request."""
    
    scope: str  # ConsentScope enum value
    provider: str
    purpose: str
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class ConsentGrant(BaseSchema):
    """Consumer grants consent."""
    
    acknowledge_terms: bool = Field(
        ..., 
        description="Consumer acknowledges the terms of data access"
    )


class ConsentRevoke(BaseSchema):
    """Consumer revokes consent."""
    
    reason: str | None = None


class ConsentResponse(IDSchema, TimestampSchema):
    """Consent response schema."""
    
    consumer_id: UUID
    case_id: UUID | None = None
    scope: str
    provider: str
    purpose: str
    status: str
    requested_at: datetime
    granted_at: datetime | None = None
    revoked_at: datetime | None = None
    expires_at: datetime | None = None
    downstream_disable_verified: bool


class ConsentEventResponse(IDSchema, TimestampSchema):
    """Consent event response."""
    
    consent_id: UUID
    event_type: str
    event_data: dict | None = None


class AccessLogEntry(IDSchema, TimestampSchema):
    """Access log entry for 1033 compliance."""
    
    accessor_type: str
    accessor_role: str | None
    resource_type: str
    action: str
    purpose: str | None


class DataExportRequest(BaseSchema):
    """Consumer data export request."""
    
    format: str = Field(default="json", pattern="^(json|csv)$")
    include_audit_log: bool = False
