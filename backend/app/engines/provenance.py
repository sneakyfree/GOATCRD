"""
GOATCRD Provenance Tracker
Tracks data source, verification status, and confidence for every field
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class ProvenanceState(str, Enum):
    """Data provenance states per GOATCRD spec."""
    
    VERIFIED = "verified"      # Confirmed by authoritative source
    PROVIDED = "provided"      # User-provided, not yet verified
    ESTIMATED = "estimated"    # Derived/imputed from other data
    UNKNOWN = "unknown"        # Required but not provided


class SourceType(str, Enum):
    """Source types for provenance."""
    
    CONSUMER_INPUT = "consumer_input"
    PAYROLL_API = "payroll_api"
    CREDIT_BUREAU = "credit_bureau"
    BANK_ACCOUNT = "bank_account"
    TAX_RETURN = "tax_return"
    EMPLOYER_VERIFICATION = "employer_verification"
    DOCUMENT_OCR = "document_ocr"
    OPEN_BANKING = "open_banking"
    ESTIMATED = "estimated"
    SYSTEM = "system"


@dataclass
class ProvenanceRecord:
    """Provenance record for a single field."""
    
    field_name: str
    state: ProvenanceState
    source_type: SourceType
    source_id: str | None = None
    source_timestamp: datetime | None = None
    confidence: int = 100  # 0-100
    value_hash: str | None = None  # For change detection
    verification_method: str | None = None
    notes: str | None = None


@dataclass
class ContradictionRecord:
    """Record of a detected contradiction."""
    
    contradiction_id: UUID
    field_name: str
    source_a: str
    value_a: Any
    source_b: str
    value_b: Any
    severity: str  # low, medium, high
    resolution: str | None = None
    resolved_by: UUID | None = None
    resolved_at: datetime | None = None


class ProvenanceTracker:
    """
    Tracks and manages data provenance across the intake lifecycle.
    
    Responsibilities:
    - Track source and verification status for each field
    - Detect contradictions between sources
    - Calculate provenance-based confidence
    - Generate verification checklists
    """
    
    def __init__(self):
        self.records: dict[str, ProvenanceRecord] = {}
        self.contradictions: list[ContradictionRecord] = []
        self.history: list[dict] = []
    
    def set_provenance(
        self,
        field_name: str,
        value: Any,
        state: ProvenanceState,
        source_type: SourceType,
        source_id: str | None = None,
        confidence: int = 100,
        verification_method: str | None = None,
    ) -> ProvenanceRecord:
        """
        Set or update provenance for a field.
        
        Returns the created/updated ProvenanceRecord.
        """
        import hashlib
        
        value_hash = hashlib.sha256(str(value).encode()).hexdigest()[:16]
        
        record = ProvenanceRecord(
            field_name=field_name,
            state=state,
            source_type=source_type,
            source_id=source_id,
            source_timestamp=datetime.now(timezone.utc),
            confidence=confidence,
            value_hash=value_hash,
            verification_method=verification_method,
        )
        
        # Check for contradictions with existing record
        if field_name in self.records:
            existing = self.records[field_name]
            if existing.value_hash != value_hash:
                self._detect_contradiction(
                    field_name=field_name,
                    existing=existing,
                    new=record,
                    old_value=None,  # Would need to store actual values
                    new_value=value,
                )
        
        # Track history
        self.history.append({
            "action": "set",
            "field_name": field_name,
            "state": state.value,
            "source_type": source_type.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        self.records[field_name] = record
        return record
    
    def upgrade_provenance(
        self,
        field_name: str,
        new_state: ProvenanceState,
        source_type: SourceType,
        source_id: str | None = None,
        verification_method: str | None = None,
    ) -> ProvenanceRecord | None:
        """
        Upgrade provenance state (e.g., from PROVIDED to VERIFIED).
        
        Only allows upgrades to higher trust levels.
        """
        if field_name not in self.records:
            return None
        
        existing = self.records[field_name]
        
        # Define trust hierarchy
        trust_order = {
            ProvenanceState.UNKNOWN: 0,
            ProvenanceState.ESTIMATED: 1,
            ProvenanceState.PROVIDED: 2,
            ProvenanceState.VERIFIED: 3,
        }
        
        if trust_order.get(new_state, 0) <= trust_order.get(existing.state, 0):
            return existing  # Can't downgrade
        
        # Upgrade
        existing.state = new_state
        existing.source_type = source_type
        existing.source_id = source_id
        existing.source_timestamp = datetime.now(timezone.utc)
        existing.verification_method = verification_method
        
        # Increase confidence for verified
        if new_state == ProvenanceState.VERIFIED:
            existing.confidence = 100
        
        self.history.append({
            "action": "upgrade",
            "field_name": field_name,
            "new_state": new_state.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        return existing
    
    def get_provenance(self, field_name: str) -> ProvenanceRecord | None:
        """Get provenance record for a field."""
        return self.records.get(field_name)
    
    def get_all_provenance(self) -> dict[str, dict]:
        """Get all provenance records as dicts for storage."""
        return {
            name: {
                "state": rec.state.value,
                "source_type": rec.source_type.value,
                "source_id": rec.source_id,
                "confidence": rec.confidence,
                "verification_method": rec.verification_method,
            }
            for name, rec in self.records.items()
        }
    
    def _detect_contradiction(
        self,
        field_name: str,
        existing: ProvenanceRecord,
        new: ProvenanceRecord,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """Detect and record a contradiction."""
        contradiction = ContradictionRecord(
            contradiction_id=uuid4(),
            field_name=field_name,
            source_a=existing.source_type.value,
            value_a=old_value,
            source_b=new.source_type.value,
            value_b=new_value,
            severity=self._calculate_severity(field_name, existing, new),
        )
        self.contradictions.append(contradiction)
    
    def _calculate_severity(
        self,
        field_name: str,
        existing: ProvenanceRecord,
        new: ProvenanceRecord,
    ) -> str:
        """Calculate contradiction severity."""
        # High-impact fields
        high_impact = {"annual_income", "credit_score", "dti_ratio"}
        if field_name in high_impact:
            return "high"
        
        # Both verified = critical
        if existing.state == ProvenanceState.VERIFIED and new.state == ProvenanceState.VERIFIED:
            return "high"
        
        return "medium"
    
    def get_contradictions(self) -> list[ContradictionRecord]:
        """Get all unresolved contradictions."""
        return [c for c in self.contradictions if c.resolution is None]
    
    def resolve_contradiction(
        self,
        contradiction_id: UUID,
        resolution: str,
        resolved_by: UUID,
    ) -> bool:
        """Resolve a contradiction."""
        for c in self.contradictions:
            if c.contradiction_id == contradiction_id:
                c.resolution = resolution
                c.resolved_by = resolved_by
                c.resolved_at = datetime.now(timezone.utc)
                return True
        return False
    
    def calculate_confidence_impact(self) -> dict[str, Any]:
        """Calculate overall confidence impact from provenance."""
        if not self.records:
            return {"score": 0, "drivers": ["No data provided"]}
        
        verified_count = sum(1 for r in self.records.values() if r.state == ProvenanceState.VERIFIED)
        provided_count = sum(1 for r in self.records.values() if r.state == ProvenanceState.PROVIDED)
        estimated_count = sum(1 for r in self.records.values() if r.state == ProvenanceState.ESTIMATED)
        unknown_count = sum(1 for r in self.records.values() if r.state == ProvenanceState.UNKNOWN)
        
        total = len(self.records)
        unresolved_contradictions = len(self.get_contradictions())
        
        # Base score
        score = 100
        drivers = []
        
        # Deductions
        if unknown_count > 0:
            score = min(score, 50)
            drivers.append(f"{unknown_count} required field(s) missing")
        
        if estimated_count > 0:
            score -= estimated_count * 10
            drivers.append(f"{estimated_count} field(s) are estimates")
        
        if unresolved_contradictions > 0:
            score = min(score, 60)
            drivers.append(f"{unresolved_contradictions} unresolved contradiction(s)")
        
        # Bonuses
        if verified_count > 0:
            drivers.append(f"{verified_count} field(s) verified from authoritative sources")
        
        return {
            "score": max(0, min(100, score)),
            "drivers": drivers,
            "breakdown": {
                "verified": verified_count,
                "provided": provided_count,
                "estimated": estimated_count,
                "unknown": unknown_count,
            },
        }
    
    def generate_verify_checklist(self) -> list[dict]:
        """Generate verification checklist for unverified fields."""
        checklist = []
        
        for name, record in self.records.items():
            if record.state == ProvenanceState.UNKNOWN:
                checklist.append({
                    "field": name,
                    "action": f"Provide {name}",
                    "priority": "required",
                })
            elif record.state == ProvenanceState.PROVIDED:
                checklist.append({
                    "field": name,
                    "action": f"Verify {name} with documentation",
                    "priority": "recommended",
                    "methods": self._get_verification_methods(name),
                })
            elif record.state == ProvenanceState.ESTIMATED:
                checklist.append({
                    "field": name,
                    "action": f"Confirm {name} (currently estimated)",
                    "priority": "recommended",
                })
        
        return checklist
    
    def _get_verification_methods(self, field_name: str) -> list[str]:
        """Get available verification methods for a field."""
        methods = {
            "annual_income": ["Payroll API", "Pay stubs", "Tax return"],
            "employer_name": ["Payroll API", "Employment verification"],
            "credit_score": ["Credit bureau pull"],
            "bank_balance": ["Bank account linking", "Bank statements"],
            "rent_payment": ["Bank account linking", "Landlord verification"],
        }
        return methods.get(field_name, ["Documentation upload"])


# Factory function
def create_provenance_tracker() -> ProvenanceTracker:
    """Create a new provenance tracker instance."""
    return ProvenanceTracker()
