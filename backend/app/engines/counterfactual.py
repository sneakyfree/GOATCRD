"""
GOATCRD Counterfactual Simulator (What-If Engine)
Simulates hypothetical changes and their impact on eligibility
"""
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.engines.scenario_builder import ScenarioBuilder, ScenarioResult, ProgramConfig
from app.engines.confidence import ConfidenceEngine
from app.models import EligibilityStatus


# Fields that cannot be simulated (protected class proxies)
PROTECTED_FIELDS = {
    "race",
    "ethnicity", 
    "gender",
    "sex",
    "religion",
    "national_origin",
    "marital_status",
    "age",
    "disability_status",
    "pregnancy_status",
    "familial_status",
}

# Fields that can be simulated
SIMULATABLE_FIELDS = {
    "credit_score": {"min": 300, "max": 850, "type": "int"},
    "credit_utilization": {"min": 0, "max": 1, "type": "float"},
    "dti_ratio": {"min": 0, "max": 1, "type": "float"},
    "annual_income": {"min": 0, "max": 10000000, "type": "int"},
    "monthly_debt_payments": {"min": 0, "max": 100000, "type": "int"},
    "loan_amount": {"min": 1000, "max": 10000000, "type": "int"},
    "term_months": {"min": 6, "max": 360, "type": "int"},
    "employment_months": {"min": 0, "max": 600, "type": "int"},
    "bankruptcy_months": {"min": 0, "max": 600, "type": "int"},
    "delinquency_months": {"min": 0, "max": 600, "type": "int"},
}


@dataclass
class StatusChange:
    """Change in eligibility status for a program."""
    
    program_id: UUID
    program_name: str
    original_status: EligibilityStatus
    simulated_status: EligibilityStatus
    changed: bool
    new_reason_codes: list[str]
    resolved_reason_codes: list[str]


@dataclass
class CounterfactualResult:
    """Result of a What-If simulation."""
    
    case_id: UUID
    hypothetical_changes: dict[str, Any]
    validated_changes: dict[str, Any]
    rejected_changes: dict[str, str]  # field -> reason
    
    status_changes: list[StatusChange]
    changes_summary: list[str]
    
    confidence: str  # low, medium, high
    confidence_reason: str
    
    disclaimer: str = (
        "This is an estimate based on hypothetical changes. "
        "Actual eligibility depends on verified information and current program terms. "
        "This is not a guarantee of approval."
    )


class CounterfactualSimulator:
    """
    What-If simulator for exploring hypothetical changes.
    
    Guardrails:
    - Never simulates protected class changes
    - All results labeled as estimates
    - Confidence caps applied for unverified hypotheticals
    """
    
    def __init__(
        self,
        programs: list[ProgramConfig],
        confidence_engine: ConfidenceEngine | None = None,
    ):
        self.programs = programs
        self.confidence_engine = confidence_engine or ConfidenceEngine()
        self.scenario_builder = ScenarioBuilder(programs, confidence_engine)
    
    def simulate(
        self,
        case_id: UUID,
        original_data: dict[str, Any],
        original_provenance: dict[str, dict],
        hypothetical_changes: dict[str, Any],
        intake_snapshot_id: UUID,
    ) -> CounterfactualResult:
        """
        Run What-If simulation with hypothetical changes.
        
        Args:
            case_id: Case ID for context
            original_data: Original intake data
            original_provenance: Original provenance records
            hypothetical_changes: Dict of field -> new value
            intake_snapshot_id: Original snapshot ID
        
        Returns:
            CounterfactualResult with status changes and summary
        """
        # Validate changes
        validated, rejected = self._validate_changes(hypothetical_changes)
        
        if not validated:
            return CounterfactualResult(
                case_id=case_id,
                hypothetical_changes=hypothetical_changes,
                validated_changes={},
                rejected_changes=rejected,
                status_changes=[],
                changes_summary=["No valid changes to simulate."],
                confidence="low",
                confidence_reason="All proposed changes were rejected.",
            )
        
        # Create simulated data
        simulated_data = {**original_data, **validated}
        
        # Create simulated provenance (all hypotheticals are "estimated")
        simulated_provenance = dict(original_provenance)
        for field in validated:
            simulated_provenance[field] = {
                "state": "estimated",
                "source": "counterfactual_simulation",
                "confidence": 50,
            }
        
        # Run original scenarios
        original_result = self.scenario_builder.build(
            intake_data=original_data,
            provenance=original_provenance,
            intake_snapshot_id=intake_snapshot_id,
        )
        
        # Run simulated scenarios
        simulated_result = self.scenario_builder.build(
            intake_data=simulated_data,
            provenance=simulated_provenance,
            intake_snapshot_id=intake_snapshot_id,
        )
        
        # Compare results
        status_changes = self._compare_results(original_result, simulated_result)
        
        # Generate summary
        changes_summary = self._generate_summary(validated, status_changes)
        
        # Calculate confidence
        confidence, confidence_reason = self._calculate_confidence(
            validated, original_provenance
        )
        
        return CounterfactualResult(
            case_id=case_id,
            hypothetical_changes=hypothetical_changes,
            validated_changes=validated,
            rejected_changes=rejected,
            status_changes=status_changes,
            changes_summary=changes_summary,
            confidence=confidence,
            confidence_reason=confidence_reason,
        )
    
    def _validate_changes(
        self,
        changes: dict[str, Any],
    ) -> tuple[dict[str, Any], dict[str, str]]:
        """
        Validate proposed changes.
        
        Returns (validated_changes, rejected_changes)
        """
        validated = {}
        rejected = {}
        
        for field, value in changes.items():
            # Check for protected fields
            if field.lower() in PROTECTED_FIELDS:
                rejected[field] = "Protected class attribute - cannot be simulated"
                continue
            
            # Check if field is simulatable
            if field not in SIMULATABLE_FIELDS:
                rejected[field] = f"Field '{field}' is not available for simulation"
                continue
            
            # Validate value range
            spec = SIMULATABLE_FIELDS[field]
            
            try:
                if spec["type"] == "int":
                    value = int(value)
                elif spec["type"] == "float":
                    value = float(value)
            except (ValueError, TypeError):
                rejected[field] = f"Invalid value type for {field}"
                continue
            
            if value < spec["min"] or value > spec["max"]:
                rejected[field] = f"Value out of range ({spec['min']} - {spec['max']})"
                continue
            
            validated[field] = value
        
        return validated, rejected
    
    def _compare_results(
        self,
        original: Any,  # ScenarioRunResult
        simulated: Any,  # ScenarioRunResult
    ) -> list[StatusChange]:
        """Compare original and simulated scenario results."""
        changes = []
        
        # Build lookup by program ID
        original_by_program = {}
        for scenario in original.eligible + original.refer + original.not_eligible:
            original_by_program[scenario.program_id] = scenario
        
        simulated_by_program = {}
        for scenario in simulated.eligible + simulated.refer + simulated.not_eligible:
            simulated_by_program[scenario.program_id] = scenario
        
        # Compare each program
        all_programs = set(original_by_program.keys()) | set(simulated_by_program.keys())
        
        for program_id in all_programs:
            orig = original_by_program.get(program_id)
            sim = simulated_by_program.get(program_id)
            
            if not orig or not sim:
                continue
            
            # Find new and resolved reason codes
            orig_codes = set(orig.reason_codes)
            sim_codes = set(sim.reason_codes)
            
            changes.append(StatusChange(
                program_id=program_id,
                program_name=orig.program_name,
                original_status=orig.status,
                simulated_status=sim.status,
                changed=orig.status != sim.status,
                new_reason_codes=list(sim_codes - orig_codes),
                resolved_reason_codes=list(orig_codes - sim_codes),
            ))
        
        return changes
    
    def _generate_summary(
        self,
        validated_changes: dict[str, Any],
        status_changes: list[StatusChange],
    ) -> list[str]:
        """Generate human-readable summary of simulation."""
        summary = []
        
        # Describe changes made
        change_descriptions = []
        for field, value in validated_changes.items():
            if field == "credit_score":
                change_descriptions.append(f"credit score to {value}")
            elif field == "credit_utilization":
                change_descriptions.append(f"credit utilization to {value * 100:.0f}%")
            elif field == "dti_ratio":
                change_descriptions.append(f"debt-to-income ratio to {value * 100:.0f}%")
            elif field == "annual_income":
                change_descriptions.append(f"annual income to ${value:,}")
            else:
                change_descriptions.append(f"{field} to {value}")
        
        if change_descriptions:
            summary.append(f"Simulated: {', '.join(change_descriptions)}")
        
        # Count improvements
        improved = [c for c in status_changes if c.changed and 
                   self._status_improved(c.original_status, c.simulated_status)]
        declined = [c for c in status_changes if c.changed and 
                   not self._status_improved(c.original_status, c.simulated_status)]
        
        if improved:
            summary.append(
                f"{len(improved)} program(s) may become more favorable."
            )
        
        if declined:
            summary.append(
                f"{len(declined)} program(s) may become less favorable."
            )
        
        if not improved and not declined:
            summary.append("No significant changes in program eligibility detected.")
        
        return summary
    
    def _status_improved(
        self,
        original: EligibilityStatus,
        simulated: EligibilityStatus,
    ) -> bool:
        """Check if status improved."""
        order = {
            EligibilityStatus.NOT_ELIGIBLE: 0,
            EligibilityStatus.REFER: 1,
            EligibilityStatus.ELIGIBLE: 2,
        }
        return order.get(simulated, 0) > order.get(original, 0)
    
    def _calculate_confidence(
        self,
        validated_changes: dict[str, Any],
        original_provenance: dict[str, dict],
    ) -> tuple[str, str]:
        """Calculate confidence level for simulation."""
        # Check how many changes are from verified fields
        verified_count = 0
        for field in validated_changes:
            if field in original_provenance:
                if original_provenance[field].get("state") == "verified":
                    verified_count += 1
        
        total_changes = len(validated_changes)
        
        if total_changes == 0:
            return "low", "No valid changes simulated."
        
        verified_ratio = verified_count / total_changes
        
        if verified_ratio > 0.7:
            return "medium", "Simulation based on verified baseline data."
        elif verified_ratio > 0.3:
            return "low", "Some baseline data is unverified, reducing confidence."
        else:
            return "low", "Most baseline data is unverified."
