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
        """Normalize intake data for consistent processing across all 10 chapters."""
        normalized = dict(data)
        
        # Ch.1: Identity & Contact — email, phone, DOB normalization
        if "email" in normalized and isinstance(normalized["email"], str):
            normalized["email"] = normalized["email"].strip().lower()
        
        if "phone" in normalized and isinstance(normalized["phone"], str):
            # Extract digits only, preserve country code
            digits = "".join(c for c in normalized["phone"] if c.isdigit())
            if len(digits) == 10:
                digits = "1" + digits  # Add US country code
            normalized["phone"] = digits
        
        if "date_of_birth" in normalized and isinstance(normalized["date_of_birth"], str):
            # Standardize to ISO 8601 (YYYY-MM-DD)
            dob = normalized["date_of_birth"].strip()
            for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%Y/%m/%d"):
                try:
                    from datetime import datetime as dt
                    parsed = dt.strptime(dob, fmt)
                    normalized["date_of_birth"] = parsed.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
        
        # Ch.1: Name trimming
        for name_field in ("first_name", "last_name", "employer_name"):
            if name_field in normalized and isinstance(normalized[name_field], str):
                normalized[name_field] = normalized[name_field].strip()
        
        # Ch.3/4/5: Numeric fields (income, assets, debts, amounts)
        numeric_fields = [
            "annual_income", "monthly_income", "loan_amount",
            "credit_score", "monthly_debt_payments", "savings_amount",
            "retirement_amount", "investment_amount", "monthly_housing_payment",
            "credit_card_balance", "auto_loan_balance", "student_loan_balance",
            "loan_amount_requested", "employment_length_months",
        ]
        for field in numeric_fields:
            if field in normalized:
                try:
                    value = normalized[field]
                    if isinstance(value, str):
                        value = value.replace("$", "").replace(",", "").strip()
                    normalized[field] = float(value)
                except (ValueError, TypeError):
                    pass
        
        # Ch.6: Percentage fields (DTI, utilization)
        percentage_fields = ["dti_ratio", "credit_utilization"]
        for field in percentage_fields:
            if field in normalized:
                try:
                    value = normalized[field]
                    if isinstance(value, str):
                        value = value.replace("%", "").strip()
                    value = float(value)
                    if value > 1:
                        value = value / 100
                    normalized[field] = value
                except (ValueError, TypeError):
                    pass
        
        # Ch.7: Geography — state code and zip normalization
        if "state" in normalized:
            normalized["state"] = str(normalized["state"]).upper().strip()[:2]
        
        if "zip_code" in normalized and isinstance(normalized["zip_code"], str):
            normalized["zip_code"] = normalized["zip_code"].strip()[:5]
        
        # Ch.3: Employment status normalization
        if "employment_status" in normalized and isinstance(normalized["employment_status"], str):
            status_map = {
                "full-time": "employed", "full time": "employed", "ft": "employed",
                "part-time": "part_time", "part time": "part_time", "pt": "part_time",
                "self-employed": "self_employed", "self employed": "self_employed",
                "retired": "retired", "unemployed": "unemployed",
            }
            raw = normalized["employment_status"].strip().lower()
            normalized["employment_status"] = status_map.get(raw, raw)
        
        # Ch.7: Housing status normalization
        if "housing_status" in normalized and isinstance(normalized["housing_status"], str):
            housing_map = {
                "own": "own", "homeowner": "own", "owner": "own",
                "rent": "rent", "renter": "rent", "renting": "rent",
                "living with family": "family", "family": "family",
            }
            raw = normalized["housing_status"].strip().lower()
            normalized["housing_status"] = housing_map.get(raw, raw)
        
        # Ch.9: Boolean coercion for consent/agreement fields
        bool_fields = ["consent_credit_check", "consent_data_sharing", "agree_terms"]
        for field in bool_fields:
            if field in normalized:
                value = normalized[field]
                if isinstance(value, str):
                    normalized[field] = value.strip().lower() in ("yes", "true", "1", "y")
        
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
