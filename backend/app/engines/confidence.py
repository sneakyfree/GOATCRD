"""
GOATCRD Confidence Engine
Calculates confidence scores with caps and verify checklists
"""
from dataclasses import dataclass, field
from typing import Any

from app.schemas.base import ProvenanceState


@dataclass
class ConfidenceResult:
    """Result of confidence calculation."""
    
    score: int  # 0-100
    drivers: list[str]
    caps_applied: list[str]
    verify_checklist: list[str]


class ConfidenceEngine:
    """
    Engine for calculating confidence scores based on data completeness,
    verification status, and provenance.
    """
    
    def __init__(
        self,
        base_confidence: int = 100,
        unknown_cap: int = 50,
        contradiction_cap: int = 60,
        estimate_penalty: int = 10,
    ):
        self.base_confidence = base_confidence
        self.unknown_cap = unknown_cap
        self.contradiction_cap = contradiction_cap
        self.estimate_penalty = estimate_penalty
    
    def calculate(
        self,
        provenance: dict[str, dict],
        contradictions: list[str] | None = None,
        required_fields: list[str] | None = None,
    ) -> ConfidenceResult:
        """
        Calculate confidence score from provenance data.
        
        Args:
            provenance: Dict of field_name -> provenance record
            contradictions: List of contradiction messages
            required_fields: List of fields required for full confidence
        
        Returns:
            ConfidenceResult with score, drivers, caps, and verify checklist
        """
        score = self.base_confidence
        drivers: list[str] = []
        caps_applied: list[str] = []
        verify_checklist: list[str] = []
        
        contradictions = contradictions or []
        required_fields = required_fields or []
        
        # Check for unknown fields
        unknown_count = 0
        estimate_count = 0
        verified_count = 0
        
        for field_name, record in provenance.items():
            state = record.get("state", ProvenanceState.UNKNOWN)
            
            if state == ProvenanceState.UNKNOWN:
                unknown_count += 1
                verify_checklist.append(f"Provide {field_name}")
            elif state == ProvenanceState.ESTIMATED:
                estimate_count += 1
                verify_checklist.append(f"Verify {field_name} (currently estimated)")
            elif state == ProvenanceState.VERIFIED:
                verified_count += 1
            elif state == ProvenanceState.PROVIDED:
                verify_checklist.append(f"Verify {field_name} with documentation")
        
        # Check missing required fields
        missing_required = [f for f in required_fields if f not in provenance]
        for field_name in missing_required:
            unknown_count += 1
            verify_checklist.append(f"Provide required field: {field_name}")
        
        # Apply caps and penalties
        if unknown_count > 0:
            caps_applied.append(f"Unknown fields ({unknown_count})")
            score = min(score, self.unknown_cap)
            drivers.append(f"{unknown_count} field(s) have unknown values")
        
        if estimate_count > 0:
            penalty = estimate_count * self.estimate_penalty
            score = max(0, score - penalty)
            drivers.append(f"{estimate_count} field(s) are estimates (-{penalty})")
        
        if len(contradictions) > 0:
            caps_applied.append(f"Contradictions detected ({len(contradictions)})")
            score = min(score, self.contradiction_cap)
            drivers.append(f"{len(contradictions)} contradiction(s) detected")
            for c in contradictions:
                verify_checklist.append(f"Resolve: {c}")
        
        # Positive drivers
        if verified_count > 0:
            drivers.append(f"{verified_count} field(s) verified from authoritative sources")
        
        return ConfidenceResult(
            score=max(0, min(100, score)),
            drivers=drivers,
            caps_applied=caps_applied,
            verify_checklist=verify_checklist,
        )


# Singleton instance with default settings
confidence_engine = ConfidenceEngine()
