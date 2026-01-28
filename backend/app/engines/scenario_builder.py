"""
GOATCRD Scenario Builder Engine
Deterministic scenario enumeration from program catalog
"""
import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.engines.rules import RulesEngine, TriageResult
from app.engines.confidence import ConfidenceEngine, ConfidenceResult
from app.models import EligibilityStatus


@dataclass
class ProgramConfig:
    """Configuration for a credit program."""
    
    program_id: UUID
    program_code: str
    program_name: str
    program_type: str
    provider_name: str
    ruleset: dict
    pricing_config: dict | None = None
    geography_constraints: list[str] = field(default_factory=list)
    required_docs: list[str] = field(default_factory=list)


@dataclass 
class ScenarioResult:
    """Result of evaluating a single scenario."""
    
    scenario_id: UUID
    dedup_key: str
    program_id: UUID
    program_name: str
    status: EligibilityStatus
    
    # Triage details
    rule_hits: list[dict]
    missing_inputs: list[str]
    reason_codes: list[str]
    
    # Confidence
    confidence_score: int
    confidence_drivers: list[str]
    confidence_caps: list[str]
    verify_checklist: list[str]
    
    # Pricing (if available)
    pricing: dict | None = None
    pricing_source: str = "unknown"


@dataclass
class ScenarioRunResult:
    """Result of a complete scenario generation run."""
    
    run_id: UUID
    intake_snapshot_id: UUID
    program_versions: dict[str, int]
    
    # Scenarios by status
    eligible: list[ScenarioResult]
    refer: list[ScenarioResult]
    not_eligible: list[ScenarioResult]
    
    # Metadata
    started_at: datetime
    completed_at: datetime
    total_scenarios: int


class ScenarioBuilder:
    """
    Builds scenario universe from intake data and program catalog.
    
    Produces deterministic, dedup-keyed scenarios for ranking.
    """
    
    def __init__(
        self,
        programs: list[ProgramConfig],
        confidence_engine: ConfidenceEngine | None = None,
    ):
        self.programs = programs
        self.confidence_engine = confidence_engine or ConfidenceEngine()
    
    def build(
        self,
        intake_data: dict[str, Any],
        provenance: dict[str, dict],
        intake_snapshot_id: UUID,
        consumer_state: str | None = None,
    ) -> ScenarioRunResult:
        """
        Build complete scenario universe.
        
        Args:
            intake_data: Normalized intake data
            provenance: Field provenance records
            intake_snapshot_id: ID of intake snapshot
            consumer_state: Consumer's state for geography filtering
        
        Returns:
            ScenarioRunResult with all scenarios
        """
        run_id = uuid4()
        started_at = datetime.now(timezone.utc)
        
        eligible: list[ScenarioResult] = []
        refer: list[ScenarioResult] = []
        not_eligible: list[ScenarioResult] = []
        program_versions: dict[str, int] = {}
        
        for program in self.programs:
            # Geography check
            if consumer_state and program.geography_constraints:
                if consumer_state not in program.geography_constraints:
                    continue
            
            # Generate scenario
            scenario = self._evaluate_program(
                program=program,
                intake_data=intake_data,
                provenance=provenance,
            )
            
            # Track version
            program_versions[str(program.program_id)] = 1
            
            # Sort by status
            if scenario.status == EligibilityStatus.ELIGIBLE:
                eligible.append(scenario)
            elif scenario.status == EligibilityStatus.REFER:
                refer.append(scenario)
            else:
                not_eligible.append(scenario)
        
        completed_at = datetime.now(timezone.utc)
        
        return ScenarioRunResult(
            run_id=run_id,
            intake_snapshot_id=intake_snapshot_id,
            program_versions=program_versions,
            eligible=eligible,
            refer=refer,
            not_eligible=not_eligible,
            started_at=started_at,
            completed_at=completed_at,
            total_scenarios=len(eligible) + len(refer) + len(not_eligible),
        )
    
    def _evaluate_program(
        self,
        program: ProgramConfig,
        intake_data: dict[str, Any],
        provenance: dict[str, dict],
    ) -> ScenarioResult:
        """Evaluate single program against intake data."""
        
        # Create dedup key
        dedup_key = self._create_dedup_key(program.program_id, intake_data)
        
        # Run rules engine
        rules_engine = RulesEngine(program.ruleset)
        triage_result = rules_engine.evaluate(intake_data)
        
        # Run confidence engine
        required_fields = self._get_required_fields(program.ruleset)
        confidence_result = self.confidence_engine.calculate(
            provenance=provenance,
            contradictions=[],  # TODO: Pass contradictions
            required_fields=required_fields,
        )
        
        # Resolve pricing if eligible
        pricing = None
        pricing_source = "unknown"
        if triage_result.status == EligibilityStatus.ELIGIBLE:
            pricing, pricing_source = self._resolve_pricing(
                program, intake_data
            )
        
        return ScenarioResult(
            scenario_id=uuid4(),
            dedup_key=dedup_key,
            program_id=program.program_id,
            program_name=program.program_name,
            status=triage_result.status,
            rule_hits=[
                {"rule_id": h.rule_id, "rule_name": h.rule_name, "passed": h.passed}
                for h in triage_result.rule_hits
            ],
            missing_inputs=triage_result.missing_inputs,
            reason_codes=triage_result.reason_codes,
            confidence_score=confidence_result.score,
            confidence_drivers=confidence_result.drivers,
            confidence_caps=confidence_result.caps_applied,
            verify_checklist=confidence_result.verify_checklist,
            pricing=pricing,
            pricing_source=pricing_source,
        )
    
    def _create_dedup_key(
        self,
        program_id: UUID,
        intake_data: dict[str, Any],
    ) -> str:
        """Create stable dedup key for scenario."""
        # Key based on program + key intake fields
        key_fields = ["annual_income", "credit_score", "dti_ratio"]
        key_values = [str(intake_data.get(f, "")) for f in sorted(key_fields)]
        key_string = f"{program_id}:{':'.join(key_values)}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _get_required_fields(self, ruleset: dict) -> list[str]:
        """Extract required fields from ruleset."""
        required = set()
        for rule in ruleset.get("rules", []):
            required.update(rule.get("required_fields", []))
        return list(required)
    
    def _resolve_pricing(
        self,
        program: ProgramConfig,
        intake_data: dict[str, Any],
    ) -> tuple[dict | None, str]:
        """
        Resolve pricing for a program.
        
        Returns (pricing_dict, source_label)
        """
        if not program.pricing_config:
            return None, "unknown"
        
        # Simplified pricing calculation
        # Production would call lender APIs or use configured rate tables
        config = program.pricing_config
        
        if config.get("type") == "fixed_rate":
            base_rate = config.get("base_rate", 0.10)
            amount = intake_data.get("loan_amount", 10000)
            term_months = intake_data.get("term_months", 36)
            
            monthly_rate = base_rate / 12
            monthly_payment = amount * (monthly_rate * (1 + monthly_rate)**term_months) / ((1 + monthly_rate)**term_months - 1)
            
            return {
                "monthly_payment": round(monthly_payment, 2),
                "apr": base_rate,
                "total_cost": round(monthly_payment * term_months, 2),
                "term_months": term_months,
                "source": "estimate",
                "confidence": 70,
            }, "estimate"
        
        return None, "unknown"


# Example program catalog
EXAMPLE_PROGRAM_CATALOG = [
    ProgramConfig(
        program_id=uuid4(),
        program_code="PL_BASIC",
        program_name="Personal Loan - Standard",
        program_type="personal_loan",
        provider_name="Example Lender",
        ruleset={
            "name": "Personal Loan Eligibility",
            "rules": [
                {
                    "id": "min_income",
                    "name": "Minimum Income",
                    "condition": "annual_income >= 24000",
                    "required_fields": ["annual_income"],
                    "reason_code": "RC004",
                },
                {
                    "id": "max_dti",
                    "name": "Maximum DTI",
                    "condition": "dti_ratio <= 0.43",
                    "required_fields": ["dti_ratio"],
                    "reason_code": "RC003",
                },
                {
                    "id": "min_score",
                    "name": "Minimum Credit Score",
                    "condition": "credit_score >= 580",
                    "required_fields": ["credit_score"],
                    "reason_code": "RC002",
                },
            ],
        },
        pricing_config={
            "type": "fixed_rate",
            "base_rate": 0.12,
        },
    ),
    ProgramConfig(
        program_id=uuid4(),
        program_code="PL_PRIME",
        program_name="Personal Loan - Prime",
        program_type="personal_loan",
        provider_name="Example Lender",
        ruleset={
            "name": "Prime Personal Loan",
            "rules": [
                {
                    "id": "min_income",
                    "name": "Minimum Income",
                    "condition": "annual_income >= 50000",
                    "required_fields": ["annual_income"],
                    "reason_code": "RC004",
                },
                {
                    "id": "max_dti",
                    "name": "Maximum DTI",
                    "condition": "dti_ratio <= 0.36",
                    "required_fields": ["dti_ratio"],
                    "reason_code": "RC003",
                },
                {
                    "id": "min_score",
                    "name": "Minimum Credit Score",
                    "condition": "credit_score >= 720",
                    "required_fields": ["credit_score"],
                    "reason_code": "RC002",
                },
            ],
        },
        pricing_config={
            "type": "fixed_rate",
            "base_rate": 0.08,
        },
    ),
]
