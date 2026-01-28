"""
GOATCRD Program Admin API Routes
CRUD operations for program catalog management
"""
from datetime import date, datetime, timezone
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, DBSession
from app.models import (
    Program,
    ProgramType,
    PricingSourceType,
    UserRole,
)
from app.services import AuditService

router = APIRouter(prefix="/admin/programs", tags=["admin", "programs"])


# --- Request/Response Schemas ---

class ProgramCreate(BaseModel):
    """Request to create a new program."""
    program_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    program_type: ProgramType
    provider_name: str | None = None
    geography_constraints: list[str] = Field(default_factory=list)
    eligibility_ruleset_id: UUID | None = None
    pricing_source: PricingSourceType = PricingSourceType.UNKNOWN
    required_docs: list[str] = Field(default_factory=list)
    disclosures: list[str] = Field(default_factory=list)
    effective_date: date


class ProgramUpdate(BaseModel):
    """Request to update a program."""
    name: str | None = None
    provider_name: str | None = None
    geography_constraints: list[str] | None = None
    eligibility_ruleset_id: UUID | None = None
    pricing_source: PricingSourceType | None = None
    required_docs: list[str] | None = None
    disclosures: list[str] | None = None
    is_active: bool | None = None


class ProgramResponse(BaseModel):
    """Program response."""
    id: UUID
    program_code: str
    name: str
    program_type: str
    provider_name: str | None
    geography_constraints: list[str]
    eligibility_ruleset_id: UUID | None
    pricing_source: str
    required_docs: list[str]
    disclosures: list[str]
    effective_date: date
    deprecated_date: date | None
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgramVersionResponse(BaseModel):
    """Program version history entry."""
    version: int
    changed_at: datetime
    changed_by: UUID | None
    changes: dict


# --- Helper ---

def require_admin(current_user: CurrentUser) -> None:
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


# --- Endpoints ---

@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    program_in: ProgramCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> Program:
    """Create a new program in the catalog."""
    require_admin(current_user)
    
    # Check for duplicate code
    result = await db.execute(
        select(Program).where(Program.program_code == program_in.program_code)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Program with code '{program_in.program_code}' already exists",
        )
    
    program = Program(
        program_code=program_in.program_code,
        name=program_in.name,
        program_type=program_in.program_type,
        provider_name=program_in.provider_name,
        geography_constraints=program_in.geography_constraints,
        eligibility_ruleset_id=program_in.eligibility_ruleset_id,
        pricing_source=program_in.pricing_source,
        required_docs=program_in.required_docs,
        disclosures=program_in.disclosures,
        effective_date=program_in.effective_date,
        is_active=True,
        version=1,
        created_by=current_user.id,
    )
    
    db.add(program)
    await db.flush()
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="program_created",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={"program_id": str(program.id), "code": program.program_code},
    )
    
    await db.refresh(program)
    return program


@router.get("", response_model=list[ProgramResponse])
async def list_programs(
    current_user: CurrentUser,
    db: DBSession,
    program_type: ProgramType | None = None,
    active_only: bool = True,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Program]:
    """List all programs with optional filters."""
    require_admin(current_user)
    
    query = select(Program)
    
    if program_type:
        query = query.where(Program.program_type == program_type)
    
    if active_only:
        query = query.where(Program.is_active == True)
    
    query = query.order_by(Program.name).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(
    program_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> Program:
    """Get a specific program by ID."""
    require_admin(current_user)
    
    result = await db.execute(
        select(Program).where(Program.id == program_id)
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    
    return program


@router.put("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: UUID,
    program_in: ProgramUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> Program:
    """Update a program (creates new version)."""
    require_admin(current_user)
    
    result = await db.execute(
        select(Program).where(Program.id == program_id)
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    
    # Track changes for audit
    changes = {}
    
    if program_in.name is not None and program_in.name != program.name:
        changes["name"] = {"old": program.name, "new": program_in.name}
        program.name = program_in.name
    
    if program_in.provider_name is not None:
        changes["provider_name"] = {"old": program.provider_name, "new": program_in.provider_name}
        program.provider_name = program_in.provider_name
    
    if program_in.geography_constraints is not None:
        changes["geography_constraints"] = {"old": program.geography_constraints, "new": program_in.geography_constraints}
        program.geography_constraints = program_in.geography_constraints
    
    if program_in.eligibility_ruleset_id is not None:
        changes["eligibility_ruleset_id"] = {"old": str(program.eligibility_ruleset_id), "new": str(program_in.eligibility_ruleset_id)}
        program.eligibility_ruleset_id = program_in.eligibility_ruleset_id
    
    if program_in.pricing_source is not None:
        changes["pricing_source"] = {"old": program.pricing_source.value, "new": program_in.pricing_source.value}
        program.pricing_source = program_in.pricing_source
    
    if program_in.required_docs is not None:
        changes["required_docs"] = {"old": program.required_docs, "new": program_in.required_docs}
        program.required_docs = program_in.required_docs
    
    if program_in.disclosures is not None:
        changes["disclosures"] = {"old": program.disclosures, "new": program_in.disclosures}
        program.disclosures = program_in.disclosures
    
    if program_in.is_active is not None:
        changes["is_active"] = {"old": program.is_active, "new": program_in.is_active}
        program.is_active = program_in.is_active
    
    if changes:
        program.version += 1
        program.updated_by = current_user.id
        
        # Audit log
        audit = AuditService(db)
        await audit.log_event(
            event_type="program_updated",
            actor_id=current_user.id,
            actor_role=current_user.role.value,
            event_data={
                "program_id": str(program.id),
                "version": program.version,
                "changes": changes,
            },
        )
    
    await db.flush()
    await db.refresh(program)
    return program


@router.delete("/{program_id}", response_model=ProgramResponse)
async def deprecate_program(
    program_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> Program:
    """Deprecate a program (soft delete)."""
    require_admin(current_user)
    
    result = await db.execute(
        select(Program).where(Program.id == program_id)
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    
    program.is_active = False
    program.deprecated_date = date.today()
    program.version += 1
    program.updated_by = current_user.id
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="program_deprecated",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={"program_id": str(program.id), "code": program.program_code},
    )
    
    await db.flush()
    await db.refresh(program)
    return program


@router.get("/{program_id}/versions", response_model=list[ProgramVersionResponse])
async def get_program_versions(
    program_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> list[dict]:
    """Get version history for a program."""
    require_admin(current_user)
    
    # Verify program exists
    result = await db.execute(
        select(Program).where(Program.id == program_id)
    )
    program = result.scalar_one_or_none()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
        )
    
    # Get version history from audit events
    from app.models import AuditEvent
    
    audit_result = await db.execute(
        select(AuditEvent).where(
            AuditEvent.event_type.in_(["program_created", "program_updated", "program_deprecated"]),
            AuditEvent.event_data["program_id"].astext == str(program_id),
        ).order_by(AuditEvent.created_at.desc())
    )
    events = list(audit_result.scalars().all())
    
    versions = []
    for event in events:
        versions.append({
            "version": event.event_data.get("version", 1),
            "changed_at": event.created_at,
            "changed_by": event.actor_id,
            "changes": event.event_data.get("changes", {}),
        })
    
    return versions
