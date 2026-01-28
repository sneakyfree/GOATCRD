"""
GOATCRD Disparate Impact Testing
Calculate adverse impact ratios for fair lending compliance
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class ProtectedClass(str, Enum):
    """Protected classes for fair lending analysis."""
    SEX = "sex"
    RACE = "race"
    AGE = "age"
    NATIONAL_ORIGIN = "national_origin"
    MARITAL_STATUS = "marital_status"


class OutcomeType(str, Enum):
    """Types of outcomes to analyze."""
    APPROVAL = "approval"
    PRICING = "pricing"
    TERMS = "terms"


@dataclass
class GroupMetrics:
    """Metrics for a demographic group."""
    group_name: str
    total_count: int
    favorable_count: int
    unfavorable_count: int
    
    @property
    def favorable_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.favorable_count / self.total_count
    
    @property
    def unfavorable_rate(self) -> float:
        if self.total_count == 0:
            return 0.0
        return self.unfavorable_count / self.total_count


@dataclass
class DisparateImpactResult:
    """Result of disparate impact analysis."""
    test_id: UUID
    protected_class: ProtectedClass
    outcome_type: OutcomeType
    
    reference_group: GroupMetrics
    comparison_groups: list[GroupMetrics]
    
    adverse_impact_ratios: dict[str, float]
    
    # 80% rule threshold
    passes_80_percent_rule: bool
    failed_groups: list[str]
    
    # Statistical significance
    sample_size_adequate: bool
    
    tested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    notes: str | None = None


def calculate_approval_rates(
    scenarios: list[dict],
    group_field: str,
    group_value: Any,
) -> GroupMetrics:
    """
    Calculate approval rates for a specific demographic group.
    
    Args:
        scenarios: List of scenario results
        group_field: Field name containing group identifier
        group_value: Value identifying this group
    
    Returns:
        GroupMetrics for the specified group
    """
    group_scenarios = [
        s for s in scenarios
        if s.get("demographics", {}).get(group_field) == group_value
    ]
    
    total = len(group_scenarios)
    favorable = len([s for s in group_scenarios if s.get("status") == "eligible"])
    unfavorable = len([s for s in group_scenarios if s.get("status") == "not_eligible"])
    
    return GroupMetrics(
        group_name=str(group_value),
        total_count=total,
        favorable_count=favorable,
        unfavorable_count=unfavorable,
    )


def calculate_adverse_impact_ratio(
    reference_rate: float,
    comparison_rate: float,
) -> float:
    """
    Calculate adverse impact ratio (AIR).
    
    AIR = comparison_group_rate / reference_group_rate
    
    Per the 80% rule, AIR < 0.80 indicates potential adverse impact.
    """
    if reference_rate == 0:
        return 0.0
    return comparison_rate / reference_rate


class DisparateImpactTest:
    """
    Disparate impact testing for fair lending compliance.
    
    Implements the 80% rule (four-fifths rule) for detecting
    potential adverse impact in credit decisions.
    """
    
    THRESHOLD = 0.80  # 80% rule threshold
    MIN_SAMPLE_SIZE = 30  # Minimum for statistical validity
    
    def __init__(self, scenarios: list[dict]):
        self.scenarios = scenarios
    
    def run_test(
        self,
        protected_class: ProtectedClass,
        outcome_type: OutcomeType = OutcomeType.APPROVAL,
        reference_group: str | None = None,
    ) -> DisparateImpactResult:
        """
        Run disparate impact test for a protected class.
        
        Args:
            protected_class: The protected class to test
            outcome_type: What outcome to analyze
            reference_group: Reference group (default: majority group)
        
        Returns:
            DisparateImpactResult with detailed metrics
        """
        # Get unique groups
        groups = self._get_groups(protected_class)
        
        if len(groups) < 2:
            return DisparateImpactResult(
                test_id=uuid4(),
                protected_class=protected_class,
                outcome_type=outcome_type,
                reference_group=GroupMetrics("unknown", 0, 0, 0),
                comparison_groups=[],
                adverse_impact_ratios={},
                passes_80_percent_rule=True,
                failed_groups=[],
                sample_size_adequate=False,
                notes="Insufficient group diversity for testing",
            )
        
        # Calculate metrics for each group
        group_metrics = {}
        for group in groups:
            metrics = calculate_approval_rates(
                self.scenarios,
                protected_class.value,
                group,
            )
            group_metrics[group] = metrics
        
        # Determine reference group (highest approval rate / majority)
        if reference_group and reference_group in group_metrics:
            ref_group = group_metrics[reference_group]
        else:
            ref_group = max(
                group_metrics.values(),
                key=lambda m: m.favorable_rate,
            )
        
        # Calculate AIR for each comparison group
        comparison_groups = [m for m in group_metrics.values() if m != ref_group]
        adverse_impact_ratios = {}
        failed_groups = []
        
        for comp_group in comparison_groups:
            air = calculate_adverse_impact_ratio(
                ref_group.favorable_rate,
                comp_group.favorable_rate,
            )
            adverse_impact_ratios[comp_group.group_name] = air
            
            if air < self.THRESHOLD and comp_group.total_count >= self.MIN_SAMPLE_SIZE:
                failed_groups.append(comp_group.group_name)
        
        # Check sample size adequacy
        total_count = sum(m.total_count for m in group_metrics.values())
        sample_adequate = total_count >= self.MIN_SAMPLE_SIZE * len(groups)
        
        return DisparateImpactResult(
            test_id=uuid4(),
            protected_class=protected_class,
            outcome_type=outcome_type,
            reference_group=ref_group,
            comparison_groups=comparison_groups,
            adverse_impact_ratios=adverse_impact_ratios,
            passes_80_percent_rule=len(failed_groups) == 0,
            failed_groups=failed_groups,
            sample_size_adequate=sample_adequate,
        )
    
    def run_all_tests(self) -> list[DisparateImpactResult]:
        """Run disparate impact tests for all protected classes."""
        results = []
        for protected_class in ProtectedClass:
            result = self.run_test(protected_class)
            results.append(result)
        return results
    
    def _get_groups(self, protected_class: ProtectedClass) -> set:
        """Get unique groups for a protected class."""
        groups = set()
        for scenario in self.scenarios:
            demographics = scenario.get("demographics", {})
            value = demographics.get(protected_class.value)
            if value:
                groups.add(value)
        return groups
