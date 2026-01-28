"""
GOATCRD Feature Auditor
Protected class proxy detection and feature risk analysis
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class RiskLevel(str, Enum):
    """Risk level for proxy variables."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


@dataclass 
class FeatureRisk:
    """Risk assessment for a single feature."""
    feature_name: str
    risk_level: RiskLevel
    
    # Correlation with protected classes
    correlations: dict[str, float]  # {protected_class: correlation_coefficient}
    
    # Risk factors
    is_geographic: bool = False
    is_name_based: bool = False
    is_demographic_proxy: bool = False
    
    recommendation: str = ""
    alternative_features: list[str] = field(default_factory=list)


@dataclass
class FeatureAuditResult:
    """Result of feature audit."""
    audit_id: UUID
    
    total_features: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    
    feature_risks: list[FeatureRisk]
    
    # Overall assessment
    passes_audit: bool
    summary: str
    
    audited_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class FeatureAuditor:
    """
    Audit features for potential protected class proxies.
    
    Identifies features that may correlate with race, sex,
    age, or other protected classes.
    """
    
    # Known high-risk features
    HIGH_RISK_FEATURES = {
        "zip_code": "Geographic proxy for race/ethnicity",
        "zip": "Geographic proxy for race/ethnicity",
        "neighborhood": "Geographic proxy for race/ethnicity",
        "first_name": "Potential proxy for sex/ethnicity",
        "last_name": "Potential proxy for ethnicity",
        "university": "Potential proxy for socioeconomic status",
        "school": "Potential proxy for socioeconomic status",
    }
    
    MEDIUM_RISK_FEATURES = {
        "city": "May correlate with demographics",
        "state": "May correlate with demographics",
        "occupation": "May correlate with sex/race",
        "industry": "May correlate with sex/race",
        "employer_type": "May correlate with demographics",
        "marital_status": "Protected class in some jurisdictions",
    }
    
    # Safe alternatives mapping
    ALTERNATIVES = {
        "zip_code": ["state", "region", "metro_area_type"],
        "first_name": ["initials_only"],
        "neighborhood": ["property_type", "building_age"],
        "university": ["degree_type", "years_since_graduation"],
    }
    
    def __init__(self, feature_names: list[str]):
        self.feature_names = feature_names
    
    def audit(self) -> FeatureAuditResult:
        """
        Audit all features for proxy risk.
        
        Returns detailed risk assessment for each feature.
        """
        feature_risks = []
        
        for feature in self.feature_names:
            risk = self._assess_feature(feature)
            feature_risks.append(risk)
        
        # Count by risk level
        high = len([f for f in feature_risks if f.risk_level == RiskLevel.HIGH])
        medium = len([f for f in feature_risks if f.risk_level == RiskLevel.MEDIUM])
        low = len([f for f in feature_risks if f.risk_level == RiskLevel.LOW])
        
        # Overall assessment
        passes = high == 0
        
        if high > 0:
            summary = f"FAIL: {high} high-risk features detected that may serve as protected class proxies"
        elif medium > 0:
            summary = f"CAUTION: {medium} medium-risk features require review"
        else:
            summary = "PASS: No significant proxy risks detected"
        
        return FeatureAuditResult(
            audit_id=uuid4(),
            total_features=len(self.feature_names),
            high_risk_count=high,
            medium_risk_count=medium,
            low_risk_count=low,
            feature_risks=feature_risks,
            passes_audit=passes,
            summary=summary,
        )
    
    def _assess_feature(self, feature: str) -> FeatureRisk:
        """Assess risk for a single feature."""
        feature_lower = feature.lower()
        
        # Check known high-risk
        for risky, reason in self.HIGH_RISK_FEATURES.items():
            if risky in feature_lower:
                return FeatureRisk(
                    feature_name=feature,
                    risk_level=RiskLevel.HIGH,
                    correlations={"unknown": 0.0},  # Would calculate from data
                    is_geographic="zip" in feature_lower or "neighborhood" in feature_lower,
                    is_name_based="name" in feature_lower,
                    is_demographic_proxy=True,
                    recommendation=f"REMOVE: {reason}",
                    alternative_features=self.ALTERNATIVES.get(risky, []),
                )
        
        # Check medium-risk
        for risky, reason in self.MEDIUM_RISK_FEATURES.items():
            if risky in feature_lower:
                return FeatureRisk(
                    feature_name=feature,
                    risk_level=RiskLevel.MEDIUM,
                    correlations={"unknown": 0.0},
                    is_demographic_proxy=True,
                    recommendation=f"REVIEW: {reason}",
                )
        
        # Check for age-related
        if any(term in feature_lower for term in ["age", "birth", "dob", "generation"]):
            return FeatureRisk(
                feature_name=feature,
                risk_level=RiskLevel.MEDIUM,
                correlations={"age": 1.0},
                recommendation="REVIEW: Direct age indicator",
            )
        
        # Low risk / safe
        return FeatureRisk(
            feature_name=feature,
            risk_level=RiskLevel.SAFE,
            correlations={},
            recommendation="OK: No obvious proxy risk",
        )
    
    def get_remediation_plan(self, audit_result: FeatureAuditResult) -> list[dict]:
        """Generate remediation plan for risky features."""
        plan = []
        
        for risk in audit_result.feature_risks:
            if risk.risk_level in (RiskLevel.HIGH, RiskLevel.MEDIUM):
                plan.append({
                    "feature": risk.feature_name,
                    "risk_level": risk.risk_level.value,
                    "action": risk.recommendation,
                    "alternatives": risk.alternative_features,
                    "priority": 1 if risk.risk_level == RiskLevel.HIGH else 2,
                })
        
        return sorted(plan, key=lambda x: x["priority"])
