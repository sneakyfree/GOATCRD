"""
GOATCRD Ruleset Admin API Routes
CRUD operations for configurable eligibility rules
"""
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.api.deps import CurrentUser, DBSession
from app.models import Ruleset, UserRole
from app.services import AuditService

router = APIRouter(prefix="/admin/rulesets", tags=["admin", "rulesets"])


# --- Request/Response Schemas ---

class RuleCondition(BaseModel):
    """Single rule condition."""
    field: str
    operator: str  # eq, ne, gt, gte, lt, lte, in, not_in, contains
    value: Any


class Rule(BaseModel):
    """Rule definition."""
    name: str
    conditions: list[RuleCondition]
    result_status: str  # eligible, refer, not_eligible
    reason_code: str | None = None
    weight: int = 100


class RulesetCreate(BaseModel):
    """Request to create a new ruleset."""
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    rules: list[Rule]


class RulesetUpdate(BaseModel):
    """Request to update a ruleset."""
    name: str | None = None
    description: str | None = None
    rules: list[Rule] | None = None
    is_active: bool | None = None


class RulesetResponse(BaseModel):
    """Ruleset response."""
    id: UUID
    name: str
    description: str | None
    rules_json: dict
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RuleTestRequest(BaseModel):
    """Request to test ruleset against sample data."""
    sample_data: dict


class RuleTestResult(BaseModel):
    """Result of ruleset test."""
    status: str
    matched_rules: list[str]
    reason_codes: list[str]
    field_results: dict[str, dict]


# --- Helper ---

def require_admin(current_user: CurrentUser) -> None:
    """Require admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )


def compile_rules(rules: list[Rule]) -> dict:
    """Compile rules list to JSON format for storage."""
    return {
        "version": "1.0",
        "rules": [rule.dict() for rule in rules],
        "compiled_at": datetime.now(timezone.utc).isoformat(),
    }


# --- Endpoints ---

@router.post("", response_model=RulesetResponse, status_code=status.HTTP_201_CREATED)
async def create_ruleset(
    ruleset_in: RulesetCreate,
    current_user: CurrentUser,
    db: DBSession,
) -> Ruleset:
    """Create a new ruleset."""
    require_admin(current_user)
    
    ruleset = Ruleset(
        name=ruleset_in.name,
        description=ruleset_in.description,
        rules_json=compile_rules(ruleset_in.rules),
        is_active=True,
        version=1,
        created_by=current_user.id,
    )
    
    db.add(ruleset)
    await db.flush()
    
    # Audit log
    audit = AuditService(db)
    await audit.log_event(
        event_type="ruleset_created",
        actor_id=current_user.id,
        actor_role=current_user.role.value,
        event_data={"ruleset_id": str(ruleset.id), "name": ruleset.name, "rule_count": len(ruleset_in.rules)},
    )
    
    await db.refresh(ruleset)
    return ruleset


@router.get("", response_model=list[RulesetResponse])
async def list_rulesets(
    current_user: CurrentUser,
    db: DBSession,
    active_only: bool = True,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
) -> list[Ruleset]:
    """List all rulesets."""
    require_admin(current_user)
    
    query = select(Ruleset)
    
    if active_only:
        query = query.where(Ruleset.is_active == True)
    
    query = query.order_by(Ruleset.name).limit(limit).offset(offset)
    
    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/{ruleset_id}", response_model=RulesetResponse)
async def get_ruleset(
    ruleset_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
) -> Ruleset:
    """Get a specific ruleset."""
    require_admin(current_user)
    
    result = await db.execute(
        select(Ruleset).where(Ruleset.id == ruleset_id)
    )
    ruleset = result.scalar_one_or_none()
    
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruleset not found",
        )
    
    return ruleset


@router.put("/{ruleset_id}", response_model=RulesetResponse)
async def update_ruleset(
    ruleset_id: UUID,
    ruleset_in: RulesetUpdate,
    current_user: CurrentUser,
    db: DBSession,
) -> Ruleset:
    """Update a ruleset (creates new version)."""
    require_admin(current_user)
    
    result = await db.execute(
        select(Ruleset).where(Ruleset.id == ruleset_id)
    )
    ruleset = result.scalar_one_or_none()
    
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruleset not found",
        )
    
    changes = {}
    
    if ruleset_in.name is not None and ruleset_in.name != ruleset.name:
        changes["name"] = {"old": ruleset.name, "new": ruleset_in.name}
        ruleset.name = ruleset_in.name
    
    if ruleset_in.description is not None:
        changes["description"] = {"old": ruleset.description, "new": ruleset_in.description}
        ruleset.description = ruleset_in.description
    
    if ruleset_in.rules is not None:
        old_count = len(ruleset.rules_json.get("rules", []))
        new_count = len(ruleset_in.rules)
        changes["rules"] = {"old_count": old_count, "new_count": new_count}
        ruleset.rules_json = compile_rules(ruleset_in.rules)
    
    if ruleset_in.is_active is not None:
        changes["is_active"] = {"old": ruleset.is_active, "new": ruleset_in.is_active}
        ruleset.is_active = ruleset_in.is_active
    
    if changes:
        ruleset.version += 1
        ruleset.updated_by = current_user.id
        
        # Audit log
        audit = AuditService(db)
        await audit.log_event(
            event_type="ruleset_updated",
            actor_id=current_user.id,
            actor_role=current_user.role.value,
            event_data={
                "ruleset_id": str(ruleset.id),
                "version": ruleset.version,
                "changes": changes,
            },
        )
    
    await db.flush()
    await db.refresh(ruleset)
    return ruleset


@router.post("/{ruleset_id}/test", response_model=RuleTestResult)
async def test_ruleset(
    ruleset_id: UUID,
    test_request: RuleTestRequest,
    current_user: CurrentUser,
    db: DBSession,
) -> dict:
    """Test a ruleset against sample data."""
    require_admin(current_user)
    
    result = await db.execute(
        select(Ruleset).where(Ruleset.id == ruleset_id)
    )
    ruleset = result.scalar_one_or_none()
    
    if not ruleset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ruleset not found",
        )
    
    # Evaluate rules against sample data
    rules = ruleset.rules_json.get("rules", [])
    matched_rules = []
    reason_codes = []
    field_results = {}
    final_status = "eligible"  # Default
    
    for rule in rules:
        rule_matched = True
        
        for condition in rule.get("conditions", []):
            field = condition["field"]
            operator = condition["operator"]
            expected = condition["value"]
            actual = test_request.sample_data.get(field)
            
            # Evaluate condition
            match_result = _evaluate_condition(actual, operator, expected)
            field_results[field] = {
                "actual": actual,
                "expected": expected,
                "operator": operator,
                "matched": match_result,
            }
            
            if not match_result:
                rule_matched = False
        
        if rule_matched:
            matched_rules.append(rule["name"])
            if rule.get("reason_code"):
                reason_codes.append(rule["reason_code"])
            
            # Check if this rule changes status
            rule_status = rule.get("result_status", "eligible")
            if rule_status == "not_eligible":
                final_status = "not_eligible"
            elif rule_status == "refer" and final_status == "eligible":
                final_status = "refer"
    
    return {
        "status": final_status,
        "matched_rules": matched_rules,
        "reason_codes": reason_codes,
        "field_results": field_results,
    }


def _evaluate_condition(actual: Any, operator: str, expected: Any) -> bool:
    """Evaluate a single condition."""
    if actual is None:
        return operator == "is_null"
    
    try:
        if operator == "eq":
            return actual == expected
        elif operator == "ne":
            return actual != expected
        elif operator == "gt":
            return float(actual) > float(expected)
        elif operator == "gte":
            return float(actual) >= float(expected)
        elif operator == "lt":
            return float(actual) < float(expected)
        elif operator == "lte":
            return float(actual) <= float(expected)
        elif operator == "in":
            return actual in expected
        elif operator == "not_in":
            return actual not in expected
        elif operator == "contains":
            return expected in str(actual)
        else:
            return False
    except (ValueError, TypeError):
        return False
