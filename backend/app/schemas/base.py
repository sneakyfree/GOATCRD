"""
GOATCRD Pydantic Schemas - Base and Common
Shared schemas and response models
"""
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""
    
    created_at: datetime
    updated_at: datetime


class IDSchema(BaseSchema):
    """Schema with UUID id."""
    
    id: UUID


# Generic type for paginated responses
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    
    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int


class SuccessResponse(BaseModel):
    """Generic success response."""
    
    success: bool = True
    message: str = "Operation completed successfully"


class ErrorResponse(BaseModel):
    """Generic error response."""
    
    success: bool = False
    error: str
    detail: str | None = None
    error_code: str | None = None


# Provenance schemas
class ProvenanceState:
    """Provenance state constants."""
    
    VERIFIED = "verified"
    PROVIDED = "provided"
    ESTIMATED = "estimated"
    UNKNOWN = "unknown"


class ProvenanceRecord(BaseSchema):
    """Data provenance record."""
    
    field_name: str
    value: Any
    state: str = Field(..., pattern="^(verified|provided|estimated|unknown)$")
    source: str
    timestamp: datetime
    confidence: int = Field(..., ge=0, le=100)
    caps_applied: list[str] = Field(default_factory=list)


class ConfidenceScore(BaseSchema):
    """Confidence scoring result."""
    
    score: int = Field(..., ge=0, le=100)
    drivers: list[str]
    caps_applied: list[str]
    verify_checklist: list[str]
