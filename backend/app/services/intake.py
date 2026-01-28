"""
GOATCRD Intake Service
Manages intake collection with provenance tracking
"""
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines.provenance import (
    ProvenanceTracker,
    ProvenanceState,
    SourceType,
    create_provenance_tracker,
)
from app.models import Case, CaseStatus, IntakeDraft, IntakeSnapshot
from app.services.audit import AuditService


class IntakeService:
    """
    Manages intake collection with provenance tracking.
    
    Responsibilities:
    - Chapter-based intake progression
    - Provenance tracking per field
    - Contradiction detection
    - Snapshot creation
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_service = AuditService(db)
    
    async def get_or_create_draft(
        self,
        case_id: UUID,
    ) -> IntakeDraft:
        """Get or create intake draft for a case."""
        result = await self.db.execute(
            select(IntakeDraft)
            .where(IntakeDraft.case_id == case_id)
            .order_by(IntakeDraft.updated_at.desc())
        )
        draft = result.scalar_one_or_none()
        
        if not draft:
            draft = IntakeDraft(
                case_id=case_id,
                data={},
                provenance={},
                current_chapter=1,
            )
            self.db.add(draft)
            await self.db.flush()
            await self.db.refresh(draft)
        
        return draft
    
    async def update_draft(
        self,
        case_id: UUID,
        field_updates: dict[str, Any],
        source_type: str = "consumer_input",
        current_chapter: int | None = None,
    ) -> IntakeDraft:
        """
        Update intake draft with new field values and provenance.
        """
        draft = await self.get_or_create_draft(case_id)
        
        # Create provenance tracker from existing data
        tracker = create_provenance_tracker()
        
        # Load existing provenance
        for field, prov in (draft.provenance or {}).items():
            if field in draft.data:
                tracker.set_provenance(
                    field_name=field,
                    value=draft.data[field],
                    state=ProvenanceState(prov.get("state", "provided")),
                    source_type=SourceType(prov.get("source_type", "consumer_input")),
                    confidence=prov.get("confidence", 100),
                )
        
        # Add new field updates with provenance
        for field, value in field_updates.items():
            tracker.set_provenance(
                field_name=field,
                value=value,
                state=ProvenanceState.PROVIDED,
                source_type=SourceType(source_type),
                confidence=80,  # User-provided starts at 80
            )
        
        # Merge data
        draft.data = {**(draft.data or {}), **field_updates}
        draft.provenance = tracker.get_all_provenance()
        draft.contradictions = [
            {
                "id": str(c.contradiction_id),
                "field": c.field_name,
                "severity": c.severity,
            }
            for c in tracker.get_contradictions()
        ]
        
        if current_chapter is not None:
            draft.current_chapter = current_chapter
        
        # Update case status
        case_result = await self.db.execute(
            select(Case).where(Case.id == case_id)
        )
        case = case_result.scalar_one_or_none()
        if case and case.status == CaseStatus.DRAFT:
            case.status = CaseStatus.INTAKE_IN_PROGRESS
        
        await self.db.flush()
        await self.db.refresh(draft)
        
        return draft
    
    async def verify_field(
        self,
        case_id: UUID,
        field_name: str,
        verified_value: Any,
        source_type: str,
        source_id: str | None = None,
        verification_method: str | None = None,
    ) -> IntakeDraft:
        """
        Verify a field from an authoritative source.
        
        Upgrades provenance state to VERIFIED.
        """
        draft = await self.get_or_create_draft(case_id)
        
        # Update data with verified value
        draft.data[field_name] = verified_value
        
        # Update provenance
        provenance = draft.provenance or {}
        provenance[field_name] = {
            "state": ProvenanceState.VERIFIED.value,
            "source_type": source_type,
            "source_id": source_id,
            "confidence": 100,
            "verification_method": verification_method,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }
        draft.provenance = provenance
        
        await self.db.flush()
        await self.db.refresh(draft)
        
        return draft
    
    async def submit_intake(
        self,
        case_id: UUID,
        actor_id: UUID,
        confirm_review: bool,
    ) -> IntakeSnapshot:
        """
        Submit intake and create immutable snapshot.
        """
        if not confirm_review:
            raise ValueError("Must confirm review before submitting")
        
        draft = await self.get_or_create_draft(case_id)
        
        if not draft.data:
            raise ValueError("No intake data to submit")
        
        # Check for unresolved high-severity contradictions
        unresolved_high = [
            c for c in (draft.contradictions or [])
            if c.get("severity") == "high" and not c.get("resolved")
        ]
        if unresolved_high:
            raise ValueError(
                f"Cannot submit with {len(unresolved_high)} unresolved high-severity contradictions"
            )
        
        # Create provenance tracker for normalization
        tracker = create_provenance_tracker()
        for field, prov in (draft.provenance or {}).items():
            if field in draft.data:
                tracker.set_provenance(
                    field_name=field,
                    value=draft.data[field],
                    state=ProvenanceState(prov.get("state", "provided")),
                    source_type=SourceType(prov.get("source_type", "consumer_input")),
                    confidence=prov.get("confidence", 80),
                )
        
        # Calculate confidence impact
        confidence_info = tracker.calculate_confidence_impact()
        
        # Normalize data (apply type coercion, format standardization)
        normalized_data = self._normalize_data(draft.data)
        
        # Create immutable snapshot
        snapshot = IntakeSnapshot(
            case_id=case_id,
            raw_data=draft.data,
            normalized_data=normalized_data,
            provenance=draft.provenance,
            contradictions_resolved=len(unresolved_high) == 0,
            created_by=actor_id,
        )
        
        self.db.add(snapshot)
        
        # Update case status
        case_result = await self.db.execute(
            select(Case).where(Case.id == case_id)
        )
        case = case_result.scalar_one_or_none()
        if case:
            case.status = CaseStatus.INTAKE_COMPLETE
        
        await self.db.flush()
        
        # Audit log
        await self.audit_service.log_intake_submitted(
            case_id=case_id,
            snapshot_id=snapshot.id,
            actor_id=actor_id,
            actor_role="consumer",
        )
        
        await self.db.refresh(snapshot)
        return snapshot
    
    def _normalize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normalize intake data for consistent processing."""
        normalized = dict(data)
        
        # Normalize numeric fields
        numeric_fields = [
            "annual_income", "monthly_income", "loan_amount",
            "credit_score", "monthly_debt_payments",
        ]
        for field in numeric_fields:
            if field in normalized:
                try:
                    value = normalized[field]
                    if isinstance(value, str):
                        # Remove currency symbols and commas
                        value = value.replace("$", "").replace(",", "").strip()
                    normalized[field] = float(value)
                except (ValueError, TypeError):
                    pass
        
        # Normalize percentage fields
        percentage_fields = ["dti_ratio", "credit_utilization"]
        for field in percentage_fields:
            if field in normalized:
                try:
                    value = normalized[field]
                    if isinstance(value, str):
                        value = value.replace("%", "").strip()
                    value = float(value)
                    # Convert to decimal if > 1 (e.g., 35% -> 0.35)
                    if value > 1:
                        value = value / 100
                    normalized[field] = value
                except (ValueError, TypeError):
                    pass
        
        # Normalize state codes
        if "state" in normalized:
            normalized["state"] = str(normalized["state"]).upper().strip()[:2]
        
        return normalized
    
    async def get_verify_checklist(
        self,
        case_id: UUID,
    ) -> list[dict]:
        """
        Get verification checklist for a case.
        """
        draft = await self.get_or_create_draft(case_id)
        
        tracker = create_provenance_tracker()
        for field, prov in (draft.provenance or {}).items():
            if field in draft.data:
                tracker.set_provenance(
                    field_name=field,
                    value=draft.data[field],
                    state=ProvenanceState(prov.get("state", "provided")),
                    source_type=SourceType(prov.get("source_type", "consumer_input")),
                    confidence=prov.get("confidence", 80),
                )
        
        return tracker.generate_verify_checklist()
