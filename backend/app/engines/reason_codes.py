"""
GOATCRD Reason Codes Engine
Maps rule hits to adverse-action-safe reason codes
"""
from dataclasses import dataclass


@dataclass
class ReasonCodeDefinition:
    """Definition of an adverse-action-safe reason code."""
    
    code: str
    category: str
    description: str
    consumer_message: str
    what_can_improve: str | None = None


# Standard GOATCRD Reason Code Catalog
REASON_CODE_CATALOG: dict[str, ReasonCodeDefinition] = {
    "RC001": ReasonCodeDefinition(
        code="RC001",
        category="Credit History",
        description="Insufficient credit history length",
        consumer_message="Your credit history may be too short for this program.",
        what_can_improve="Building credit history over time may help. Consider becoming an authorized user or using a secured credit card.",
    ),
    "RC002": ReasonCodeDefinition(
        code="RC002",
        category="Credit Score",
        description="Credit score below program threshold",
        consumer_message="Your credit score may be below the minimum for this program.",
        what_can_improve="Paying bills on time and reducing credit utilization may help improve your score over time.",
    ),
    "RC003": ReasonCodeDefinition(
        code="RC003",
        category="Debt-to-Income",
        description="Debt-to-income ratio exceeds maximum",
        consumer_message="Your current debt obligations relative to income may be too high.",
        what_can_improve="Paying down existing debt or increasing income may improve your debt-to-income ratio.",
    ),
    "RC004": ReasonCodeDefinition(
        code="RC004",
        category="Income",
        description="Income below program minimum",
        consumer_message="Your reported income may be below the minimum for this program.",
        what_can_improve="Some programs have lower income requirements. You may also verify additional income sources.",
    ),
    "RC005": ReasonCodeDefinition(
        code="RC005",
        category="Income Verification",
        description="Unable to verify income",
        consumer_message="We were unable to verify your income from the information provided.",
        what_can_improve="Providing documentation such as pay stubs or tax returns may help verify your income.",
    ),
    "RC006": ReasonCodeDefinition(
        code="RC006",
        category="Payment History",
        description="Recent delinquency on credit report",
        consumer_message="Your credit report shows recent late or missed payments.",
        what_can_improve="Maintaining on-time payments going forward may help. Older delinquencies have less impact.",
    ),
    "RC007": ReasonCodeDefinition(
        code="RC007",
        category="Bankruptcy",
        description="Recent bankruptcy filing",
        consumer_message="A recent bankruptcy filing appears on your record.",
        what_can_improve="Time since bankruptcy is often a factor. Some programs become available after the bankruptcy ages.",
    ),
    "RC008": ReasonCodeDefinition(
        code="RC008",
        category="Geography",
        description="Program not available in your state",
        consumer_message="This program is not available in your state.",
        what_can_improve="Other programs may be available in your state. Check the scenario list for alternatives.",
    ),
    "RC009": ReasonCodeDefinition(
        code="RC009",
        category="Verification",
        description="Missing required verification",
        consumer_message="Additional verification is needed to complete your evaluation.",
        what_can_improve="Providing the requested documentation will allow us to complete your evaluation.",
    ),
    "RC010": ReasonCodeDefinition(
        code="RC010",
        category="Credit Utilization",
        description="Credit utilization too high",
        consumer_message="Your credit card balances may be too high relative to your credit limits.",
        what_can_improve="Paying down credit card balances may improve your credit utilization ratio.",
    ),
    "RC011": ReasonCodeDefinition(
        code="RC011",
        category="Employment",
        description="Employment duration too short",
        consumer_message="Your current employment duration may be too short for this program.",
        what_can_improve="Some programs require longer employment history. Time in your current role may help.",
    ),
    "RC012": ReasonCodeDefinition(
        code="RC012",
        category="Collections",
        description="Active collections on credit report",
        consumer_message="Your credit report shows active collection accounts.",
        what_can_improve="Addressing collection accounts may help. Some programs exclude paid collections.",
    ),
}


class ReasonCodesEngine:
    """
    Maps rule hits to adverse-action-safe reason codes.
    
    Generates consumer-safe messages and improvement suggestions.
    """
    
    def __init__(self, catalog: dict[str, ReasonCodeDefinition] | None = None):
        self.catalog = catalog or REASON_CODE_CATALOG
    
    def get_reason_code(self, code: str) -> ReasonCodeDefinition | None:
        """Get reason code definition by code."""
        return self.catalog.get(code)
    
    def map_rule_hits_to_codes(
        self,
        rule_hits: list[dict],
    ) -> list[ReasonCodeDefinition]:
        """
        Map rule hits to reason code definitions.
        
        Args:
            rule_hits: List of rule hit dicts with 'reason_code' field
        
        Returns:
            List of ReasonCodeDefinition for failed rules
        """
        codes = []
        seen = set()
        
        for hit in rule_hits:
            # Only include failed rules
            if hit.get("passed", True):
                continue
            
            reason_code = hit.get("reason_code")
            if reason_code and reason_code not in seen:
                definition = self.catalog.get(reason_code)
                if definition:
                    codes.append(definition)
                    seen.add(reason_code)
        
        return codes
    
    def generate_adverse_action_summary(
        self,
        reason_codes: list[str],
        max_codes: int = 4,
    ) -> dict:
        """
        Generate adverse action notice summary.
        
        Args:
            reason_codes: List of reason code strings
            max_codes: Maximum number of codes to include
        
        Returns:
            Dict with consumer-safe messages and improvement suggestions
        """
        definitions = []
        for code in reason_codes[:max_codes]:
            defn = self.catalog.get(code)
            if defn:
                definitions.append(defn)
        
        if not definitions:
            return {
                "reasons": [],
                "improvements": [],
                "disclaimer": "This assessment is based on the information provided.",
            }
        
        reasons = [
            {
                "code": d.code,
                "category": d.category,
                "message": d.consumer_message,
            }
            for d in definitions
        ]
        
        improvements = [
            d.what_can_improve
            for d in definitions
            if d.what_can_improve
        ]
        
        return {
            "reasons": reasons,
            "improvements": improvements,
            "disclaimer": (
                "This is an assessment based on the information provided. "
                "Improving these factors may help your eligibility over time. "
                "This is not a guarantee of future approval."
            ),
        }
    
    def get_improvement_path(
        self,
        reason_codes: list[str],
    ) -> list[dict]:
        """
        Generate prioritized improvement path from reason codes.
        
        Returns list of improvement actions ordered by potential impact.
        """
        improvements = []
        
        # Priority order of improvements
        priority_order = [
            "RC006",  # Payment history - often big impact
            "RC010",  # Credit utilization - quick win
            "RC003",  # DTI - actionable
            "RC002",  # Credit score - general
            "RC009",  # Verification - immediate
            "RC004",  # Income
            "RC005",  # Income verification
            "RC001",  # Credit history length
            "RC011",  # Employment duration
            "RC007",  # Bankruptcy - time-based
            "RC012",  # Collections
            "RC008",  # Geography - can't change
        ]
        
        # Sort codes by priority
        sorted_codes = sorted(
            reason_codes,
            key=lambda c: priority_order.index(c) if c in priority_order else 99
        )
        
        for code in sorted_codes:
            defn = self.catalog.get(code)
            if defn and defn.what_can_improve:
                improvements.append({
                    "code": code,
                    "category": defn.category,
                    "action": defn.what_can_improve,
                    "timeframe": self._estimate_timeframe(code),
                })
        
        return improvements
    
    def _estimate_timeframe(self, code: str) -> str:
        """Estimate timeframe for improvement action."""
        quick_wins = {"RC009", "RC010", "RC005"}
        medium_term = {"RC003", "RC006", "RC012"}
        long_term = {"RC001", "RC002", "RC007", "RC011"}
        
        if code in quick_wins:
            return "weeks"
        elif code in medium_term:
            return "months"
        elif code in long_term:
            return "6+ months"
        else:
            return "varies"


# Singleton instance
reason_codes_engine = ReasonCodesEngine()
