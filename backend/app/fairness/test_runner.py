"""
GOATCRD Fairness Test Runner
CI/CD integration for automated fairness testing
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from app.fairness.disparate_impact import DisparateImpactTest, ProtectedClass
from app.fairness.lda_search import LDASearchEngine
from app.fairness.feature_audit import FeatureAuditor


class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class FairnessTestResult:
    """Comprehensive fairness test result."""
    test_run_id: UUID
    model_version: str
    rules_version: str
    
    # Individual test results
    disparate_impact_passed: bool
    feature_audit_passed: bool
    lda_available: bool
    
    # Detailed results
    disparate_impact_results: list[dict]
    feature_audit_result: dict
    lda_result: dict | None
    
    # Overall
    overall_status: TestStatus
    blocking_issues: list[str]
    warnings: list[str]
    
    # Metadata
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    
    # Approval
    requires_approval: bool = True
    approved_by: UUID | None = None
    approval_notes: str | None = None


class FairnessTestRunner:
    """
    Run comprehensive fairness test suite.
    
    Integrates with CI/CD pipeline for automated testing
    before model deployment.
    """
    
    def __init__(
        self,
        model_version: str,
        rules_version: str,
        scenarios: list[dict],
        feature_names: list[str],
    ):
        self.model_version = model_version
        self.rules_version = rules_version
        self.scenarios = scenarios
        self.feature_names = feature_names
        
        self.test_run_id = uuid4()
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
    
    def run_full_suite(self) -> FairnessTestResult:
        """
        Run complete fairness test suite.
        
        Includes:
        - Disparate impact testing for all protected classes
        - Feature proxy audit
        - LDA search if disparate impact fails
        
        Returns comprehensive result for CI/CD gate decision.
        """
        self.started_at = datetime.now(timezone.utc)
        
        blocking_issues = []
        warnings = []
        
        # 1. Run disparate impact tests
        di_test = DisparateImpactTest(self.scenarios)
        di_results = di_test.run_all_tests()
        
        di_passed = all(r.passes_80_percent_rule for r in di_results)
        
        for result in di_results:
            if not result.passes_80_percent_rule:
                blocking_issues.append(
                    f"Disparate impact detected for {result.protected_class.value}: "
                    f"groups {result.failed_groups} below 80% threshold"
                )
            elif not result.sample_size_adequate:
                warnings.append(
                    f"Insufficient sample size for {result.protected_class.value} testing"
                )
        
        # 2. Run feature audit
        auditor = FeatureAuditor(self.feature_names)
        audit_result = auditor.audit()
        
        feature_passed = audit_result.passes_audit
        
        if not feature_passed:
            blocking_issues.append(audit_result.summary)
        elif audit_result.medium_risk_count > 0:
            warnings.append(f"{audit_result.medium_risk_count} medium-risk features need review")
        
        # 3. Run LDA search if DI failed
        lda_result = None
        lda_available = False
        
        if not di_passed:
            # Find worst AIR
            worst_air = min(
                (r.adverse_impact_ratios.get(g, 1.0) 
                 for r in di_results 
                 for g in r.failed_groups),
                default=1.0
            )
            
            # Search for alternatives
            lda_engine = LDASearchEngine(
                current_air=worst_air,
                current_approval_rate=self._calculate_overall_approval_rate(),
            )
            lda_search_result = lda_engine.search()
            
            lda_available = lda_search_result.best_alternative is not None
            lda_result = {
                "search_id": str(lda_search_result.search_id),
                "alternatives_found": lda_search_result.alternatives_found,
                "recommendation": lda_search_result.recommendation,
                "best_alternative": (
                    lda_search_result.best_alternative.model_id
                    if lda_search_result.best_alternative
                    else None
                ),
            }
        
        # Determine overall status
        if blocking_issues:
            overall_status = TestStatus.FAILED
        elif warnings:
            overall_status = TestStatus.WARNING
        else:
            overall_status = TestStatus.PASSED
        
        self.completed_at = datetime.now(timezone.utc)
        duration = (self.completed_at - self.started_at).total_seconds()
        
        return FairnessTestResult(
            test_run_id=self.test_run_id,
            model_version=self.model_version,
            rules_version=self.rules_version,
            disparate_impact_passed=di_passed,
            feature_audit_passed=feature_passed,
            lda_available=lda_available,
            disparate_impact_results=[
                {
                    "protected_class": r.protected_class.value,
                    "passed": r.passes_80_percent_rule,
                    "failed_groups": r.failed_groups,
                    "adverse_impact_ratios": r.adverse_impact_ratios,
                }
                for r in di_results
            ],
            feature_audit_result={
                "audit_id": str(audit_result.audit_id),
                "passed": audit_result.passes_audit,
                "high_risk_count": audit_result.high_risk_count,
                "medium_risk_count": audit_result.medium_risk_count,
                "summary": audit_result.summary,
            },
            lda_result=lda_result,
            overall_status=overall_status,
            blocking_issues=blocking_issues,
            warnings=warnings,
            started_at=self.started_at,
            completed_at=self.completed_at,
            duration_seconds=duration,
            requires_approval=overall_status != TestStatus.PASSED,
        )
    
    def _calculate_overall_approval_rate(self) -> float:
        """Calculate overall approval rate."""
        if not self.scenarios:
            return 0.0
        
        eligible = len([s for s in self.scenarios if s.get("status") == "eligible"])
        return eligible / len(self.scenarios)


def run_ci_cd_gate(
    model_version: str,
    rules_version: str,
    scenarios: list[dict],
    feature_names: list[str],
) -> tuple[bool, dict]:
    """
    CI/CD gate function for deployment pipelines.
    
    Returns:
        Tuple of (should_deploy, details)
    """
    runner = FairnessTestRunner(
        model_version=model_version,
        rules_version=rules_version,
        scenarios=scenarios,
        feature_names=feature_names,
    )
    
    result = runner.run_full_suite()
    
    should_deploy = result.overall_status in (TestStatus.PASSED, TestStatus.WARNING)
    
    details = {
        "test_run_id": str(result.test_run_id),
        "status": result.overall_status.value,
        "blocking_issues": result.blocking_issues,
        "warnings": result.warnings,
        "duration_seconds": result.duration_seconds,
        "requires_approval": result.requires_approval,
    }
    
    return should_deploy, details
