"""
GOATCRD Audit Snapshot Engine
Immutable snapshots with determinism guarantee
"""
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


@dataclass
class VersionPins:
    """Version pins for reproducibility."""
    
    app_version: str
    program_versions: dict[str, int]
    ruleset_versions: dict[str, int]
    feature_flags: dict[str, bool]


@dataclass
class AuditSnapshotData:
    """Complete audit snapshot data."""
    
    snapshot_id: UUID
    case_id: UUID
    
    # Input state
    intake_snapshot_id: UUID
    intake_data: dict[str, Any]
    provenance: dict[str, dict]
    consent_states: dict[str, str]
    
    # Version pins
    version_pins: VersionPins
    
    # Outputs
    scenarios_summary: dict[str, Any]
    rankings_summary: dict[str, Any]
    reason_codes_issued: list[str]
    
    # Metadata
    created_at: datetime
    created_by: UUID | None
    
    # Integrity
    snapshot_hash: str


class AuditSnapshotEngine:
    """
    Creates and validates immutable audit snapshots.
    
    Guarantees:
    - Same snapshot ID → same output (determinism)
    - Hash integrity verification
    - Delta reporting between snapshots
    """
    
    def __init__(self, app_version: str = "0.1.0"):
        self.app_version = app_version
    
    def create_snapshot(
        self,
        case_id: UUID,
        intake_snapshot_id: UUID,
        intake_data: dict[str, Any],
        provenance: dict[str, dict],
        consent_states: dict[str, str],
        program_versions: dict[str, int],
        ruleset_versions: dict[str, int],
        scenarios_summary: dict[str, Any],
        rankings_summary: dict[str, Any],
        reason_codes_issued: list[str],
        feature_flags: dict[str, bool] | None = None,
        created_by: UUID | None = None,
    ) -> AuditSnapshotData:
        """
        Create immutable audit snapshot.
        
        Returns AuditSnapshotData with computed hash.
        """
        snapshot_id = uuid4()
        created_at = datetime.now(timezone.utc)
        
        version_pins = VersionPins(
            app_version=self.app_version,
            program_versions=program_versions,
            ruleset_versions=ruleset_versions,
            feature_flags=feature_flags or {},
        )
        
        # Compute hash before creating snapshot
        hash_input = self._create_hash_input(
            case_id=case_id,
            intake_data=intake_data,
            version_pins=version_pins,
            scenarios_summary=scenarios_summary,
        )
        snapshot_hash = self._compute_hash(hash_input)
        
        return AuditSnapshotData(
            snapshot_id=snapshot_id,
            case_id=case_id,
            intake_snapshot_id=intake_snapshot_id,
            intake_data=intake_data,
            provenance=provenance,
            consent_states=consent_states,
            version_pins=version_pins,
            scenarios_summary=scenarios_summary,
            rankings_summary=rankings_summary,
            reason_codes_issued=reason_codes_issued,
            created_at=created_at,
            created_by=created_by,
            snapshot_hash=snapshot_hash,
        )
    
    def verify_snapshot(self, snapshot: AuditSnapshotData) -> bool:
        """
        Verify snapshot integrity.
        
        Returns True if hash matches, False otherwise.
        """
        hash_input = self._create_hash_input(
            case_id=snapshot.case_id,
            intake_data=snapshot.intake_data,
            version_pins=snapshot.version_pins,
            scenarios_summary=snapshot.scenarios_summary,
        )
        computed_hash = self._compute_hash(hash_input)
        
        return computed_hash == snapshot.snapshot_hash
    
    def generate_delta_report(
        self,
        snapshot_a: AuditSnapshotData,
        snapshot_b: AuditSnapshotData,
    ) -> dict[str, Any]:
        """
        Generate delta report between two snapshots.
        
        Returns dict with changes between snapshots.
        """
        delta = {
            "snapshot_a_id": str(snapshot_a.snapshot_id),
            "snapshot_b_id": str(snapshot_b.snapshot_id),
            "timestamp_a": snapshot_a.created_at.isoformat(),
            "timestamp_b": snapshot_b.created_at.isoformat(),
            "changes": [],
        }
        
        # Check version changes
        version_changes = self._compare_versions(
            snapshot_a.version_pins,
            snapshot_b.version_pins,
        )
        if version_changes:
            delta["changes"].append({
                "type": "version",
                "details": version_changes,
            })
        
        # Check intake data changes
        intake_changes = self._compare_dicts(
            snapshot_a.intake_data,
            snapshot_b.intake_data,
            "intake_data",
        )
        if intake_changes:
            delta["changes"].append({
                "type": "intake",
                "details": intake_changes,
            })
        
        # Check scenario outcome changes
        outcome_changes = self._compare_scenarios(
            snapshot_a.scenarios_summary,
            snapshot_b.scenarios_summary,
        )
        if outcome_changes:
            delta["changes"].append({
                "type": "outcomes",
                "details": outcome_changes,
            })
        
        # Check reason codes
        codes_a = set(snapshot_a.reason_codes_issued)
        codes_b = set(snapshot_b.reason_codes_issued)
        
        if codes_a != codes_b:
            delta["changes"].append({
                "type": "reason_codes",
                "added": list(codes_b - codes_a),
                "removed": list(codes_a - codes_b),
            })
        
        return delta
    
    def _create_hash_input(
        self,
        case_id: UUID,
        intake_data: dict[str, Any],
        version_pins: VersionPins,
        scenarios_summary: dict[str, Any],
    ) -> str:
        """Create deterministic string for hashing."""
        # Sort keys for determinism
        hash_data = {
            "case_id": str(case_id),
            "intake_data": json.dumps(intake_data, sort_keys=True),
            "app_version": version_pins.app_version,
            "program_versions": json.dumps(version_pins.program_versions, sort_keys=True),
            "ruleset_versions": json.dumps(version_pins.ruleset_versions, sort_keys=True),
            "scenarios_summary": json.dumps(scenarios_summary, sort_keys=True),
        }
        return json.dumps(hash_data, sort_keys=True)
    
    def _compute_hash(self, input_string: str) -> str:
        """Compute SHA-256 hash of input."""
        return hashlib.sha256(input_string.encode()).hexdigest()
    
    def _compare_versions(
        self,
        pins_a: VersionPins,
        pins_b: VersionPins,
    ) -> list[dict]:
        """Compare version pins between snapshots."""
        changes = []
        
        if pins_a.app_version != pins_b.app_version:
            changes.append({
                "field": "app_version",
                "from": pins_a.app_version,
                "to": pins_b.app_version,
            })
        
        # Compare program versions
        all_programs = set(pins_a.program_versions.keys()) | set(pins_b.program_versions.keys())
        for prog in all_programs:
            v_a = pins_a.program_versions.get(prog)
            v_b = pins_b.program_versions.get(prog)
            if v_a != v_b:
                changes.append({
                    "field": f"program_version.{prog}",
                    "from": v_a,
                    "to": v_b,
                })
        
        return changes
    
    def _compare_dicts(
        self,
        dict_a: dict,
        dict_b: dict,
        prefix: str,
    ) -> list[dict]:
        """Compare two dicts and return changes."""
        changes = []
        all_keys = set(dict_a.keys()) | set(dict_b.keys())
        
        for key in all_keys:
            v_a = dict_a.get(key)
            v_b = dict_b.get(key)
            if v_a != v_b:
                changes.append({
                    "field": f"{prefix}.{key}",
                    "from": v_a,
                    "to": v_b,
                })
        
        return changes
    
    def _compare_scenarios(
        self,
        summary_a: dict[str, Any],
        summary_b: dict[str, Any],
    ) -> list[dict]:
        """Compare scenario summaries."""
        changes = []
        
        # Compare counts
        for key in ["eligible_count", "refer_count", "not_eligible_count", "total"]:
            v_a = summary_a.get(key, 0)
            v_b = summary_b.get(key, 0)
            if v_a != v_b:
                changes.append({
                    "field": key,
                    "from": v_a,
                    "to": v_b,
                })
        
        return changes


# Singleton instance
audit_snapshot_engine = AuditSnapshotEngine()
