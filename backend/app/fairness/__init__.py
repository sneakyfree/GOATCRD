"""
GOATCRD Fairness Testing Package
Fair lending compliance and disparate impact analysis
"""
from app.fairness.disparate_impact import (
    DisparateImpactTest,
    calculate_approval_rates,
    calculate_adverse_impact_ratio,
)
from app.fairness.lda_search import LDASearchEngine
from app.fairness.feature_audit import FeatureAuditor
from app.fairness.test_runner import FairnessTestRunner

__all__ = [
    "DisparateImpactTest",
    "calculate_approval_rates",
    "calculate_adverse_impact_ratio",
    "LDASearchEngine",
    "FeatureAuditor", 
    "FairnessTestRunner",
]
