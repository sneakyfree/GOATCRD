"""
GOATCRD Rules Engine
Deterministic eligibility rule evaluation
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.models import EligibilityStatus


@dataclass
class RuleHit:
    """Result of a single rule evaluation."""
    
    rule_id: str
    rule_name: str
    passed: bool
    message: str
    reason_code: str | None = None


@dataclass
class TriageResult:
    """Result of eligibility triage."""
    
    status: EligibilityStatus
    rule_hits: list[RuleHit]
    missing_inputs: list[str]
    reason_codes: list[str]
    confidence_impact: int  # How much this affects confidence


class RulesEngine:
    """
    Deterministic rules engine for eligibility triage.
    
    Rules are config-driven (YAML/JSON) and compiled into evaluators.
    """
    
    def __init__(self, ruleset: dict):
        """
        Initialize with a ruleset definition.
        
        Args:
            ruleset: Dict with 'rules' list, each rule having:
                - id: str
                - name: str
                - condition: str (expression)
                - required_fields: list[str]
                - reason_code: str (if fails)
        """
        self.ruleset = ruleset
        self.rules = ruleset.get("rules", [])
    
    def evaluate(self, data: dict[str, Any]) -> TriageResult:
        """
        Evaluate all rules against provided data.
        
        Returns TriageResult with status and rule hits.
        """
        rule_hits: list[RuleHit] = []
        missing_inputs: list[str] = []
        reason_codes: list[str] = []
        has_failure = False
        has_missing = False
        
        for rule in self.rules:
            # Check required fields
            required = rule.get("required_fields", [])
            missing = [f for f in required if f not in data or data[f] is None]
            
            if missing:
                missing_inputs.extend(missing)
                has_missing = True
                continue
            
            # Evaluate condition
            try:
                passed = self._evaluate_condition(rule["condition"], data)
            except Exception:
                # Evaluation error = treat as missing
                has_missing = True
                continue
            
            hit = RuleHit(
                rule_id=rule["id"],
                rule_name=rule["name"],
                passed=passed,
                message=rule.get("fail_message", f"Rule {rule['name']} failed") if not passed else "",
                reason_code=rule.get("reason_code") if not passed else None,
            )
            rule_hits.append(hit)
            
            if not passed:
                has_failure = True
                if hit.reason_code:
                    reason_codes.append(hit.reason_code)
        
        # Determine status
        if has_failure:
            status = EligibilityStatus.NOT_ELIGIBLE
        elif has_missing:
            status = EligibilityStatus.REFER
        else:
            status = EligibilityStatus.ELIGIBLE
        
        # Calculate confidence impact
        confidence_impact = 0
        if has_missing:
            confidence_impact = -20 * len(set(missing_inputs))
        
        return TriageResult(
            status=status,
            rule_hits=rule_hits,
            missing_inputs=list(set(missing_inputs)),
            reason_codes=reason_codes,
            confidence_impact=min(confidence_impact, 0),
        )
    
    def _evaluate_condition(self, condition: str, data: dict[str, Any]) -> bool:
        """
        Safely evaluate a condition expression.
        
        IMPORTANT: This is a simplified implementation.
        Production should use a proper expression parser (e.g., pyparsing)
        to prevent injection attacks.
        """
        # Simple evaluator for basic conditions
        # Format: "field operator value"
        parts = condition.split()
        
        if len(parts) != 3:
            raise ValueError(f"Invalid condition format: {condition}")
        
        field, operator, value = parts
        
        if field not in data:
            raise KeyError(f"Field not found: {field}")
        
        field_value = data[field]
        
        # Convert value to appropriate type
        try:
            if value.lower() == "true":
                compare_value = True
            elif value.lower() == "false":
                compare_value = False
            elif "." in value:
                compare_value = float(value)
            else:
                compare_value = int(value)
        except ValueError:
            compare_value = value.strip('"\'')
        
        # Evaluate
        if operator == ">=":
            return field_value >= compare_value
        elif operator == "<=":
            return field_value <= compare_value
        elif operator == ">":
            return field_value > compare_value
        elif operator == "<":
            return field_value < compare_value
        elif operator == "==":
            return field_value == compare_value
        elif operator == "!=":
            return field_value != compare_value
        else:
            raise ValueError(f"Unknown operator: {operator}")


# Default ruleset for personal loans (example)
DEFAULT_PERSONAL_LOAN_RULESET = {
    "name": "Personal Loan Eligibility",
    "version": "1.0.0",
    "rules": [
        {
            "id": "min_income",
            "name": "Minimum Income",
            "condition": "annual_income >= 24000",
            "required_fields": ["annual_income"],
            "reason_code": "RC004",
            "fail_message": "Annual income below minimum threshold",
        },
        {
            "id": "max_dti",
            "name": "Maximum Debt-to-Income",
            "condition": "dti_ratio <= 0.43",
            "required_fields": ["dti_ratio"],
            "reason_code": "RC003",
            "fail_message": "Debt-to-income ratio exceeds maximum",
        },
        {
            "id": "min_credit_score",
            "name": "Minimum Credit Score",
            "condition": "credit_score >= 580",
            "required_fields": ["credit_score"],
            "reason_code": "RC002",
            "fail_message": "Credit score below minimum threshold",
        },
        {
            "id": "no_recent_bankruptcy",
            "name": "No Recent Bankruptcy",
            "condition": "bankruptcy_months >= 48",
            "required_fields": ["bankruptcy_months"],
            "reason_code": "RC007",
            "fail_message": "Bankruptcy within the last 48 months",
        },
    ],
}
