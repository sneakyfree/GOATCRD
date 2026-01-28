"""
GOATCRD Explainability Engine
Generates 4-layer explanations with no-new-facts enforcement
"""
from dataclasses import dataclass
from string import Template
from typing import Any


@dataclass
class Explanation:
    """Single explanation layer."""
    
    layer: str  # consumer, pro, compliance, deep
    content: str
    field_references: list[str]


class NoNewFactsViolation(Exception):
    """Raised when a template references fields not in the data."""
    pass


class ExplainabilityEngine:
    """
    Generates explanations across 4 layers with no-new-facts enforcement.
    
    Templates can only reference stored fields; no invented claims allowed.
    """
    
    # Default templates
    CONSUMER_TEMPLATES = {
        "eligible": """
Based on the information you provided, you may be eligible for {program_name}.

Key factors that helped:
{positive_factors}

Your estimated monthly payment could be around ${estimated_payment}/month.

Next steps:
{next_steps}

*This is an estimate, not an approval. Final terms depend on verification and lender review.*
""",
        "refer": """
We need a bit more information before we can evaluate {program_name}.

What's missing:
{missing_items}

Why this matters:
{why_matters}

*Once you provide this information, we can give you a more complete picture.*
""",
        "not_eligible": """
Based on the information provided, you may not currently qualify for {program_name}.

Here's why:
{reason_summary}

What could help:
{improvement_suggestions}

*This assessment is based on the information available. Your situation may change over time.*
""",
    }
    
    PRO_TEMPLATES = {
        "eligible": """
**Eligibility Status: ELIGIBLE**

Program: {program_name}
Consumer: {consumer_name}

**Compliance-Safe Talking Points:**
{talking_points}

**Workflow Checklist:**
{workflow_items}

**Key Metrics:**
- Confidence Score: {confidence_score}%
- Pricing Source: {pricing_source}
""",
        "refer": """
**Eligibility Status: REFER**

Program: {program_name}
Reason: Additional verification required

**Action Items:**
{verification_checklist}

**Do NOT convey approval until verification complete.**
""",
        "not_eligible": """
**Eligibility Status: NOT ELIGIBLE**

Program: {program_name}

**Reason Codes:**
{reason_codes}

**Compliant Explanation for Consumer:**
{consumer_explanation}

**Improvement Path (directional only):**
{improvement_path}
""",
    }
    
    def __init__(self, data: dict[str, Any]):
        """
        Initialize with case data.
        
        Args:
            data: All available data fields (from snapshot)
        """
        self.data = data
        self.available_fields = set(data.keys())
    
    def generate(
        self,
        status: str,
        layer: str,
        context: dict[str, Any],
    ) -> Explanation:
        """
        Generate an explanation for a specific layer.
        
        Args:
            status: eligible, refer, or not_eligible
            layer: consumer, pro, compliance, or deep
            context: Additional context for template rendering
        
        Returns:
            Explanation with content and field references
        
        Raises:
            NoNewFactsViolation: If template references unknown fields
        """
        # Merge data with context
        template_data = {**self.data, **context}
        
        # Get template
        if layer == "consumer":
            templates = self.CONSUMER_TEMPLATES
        elif layer == "pro":
            templates = self.PRO_TEMPLATES
        else:
            # Compliance and deep use structured output
            return self._generate_structured(status, layer, template_data)
        
        template_str = templates.get(status, templates.get("refer", ""))
        
        # Validate no new facts
        field_references = self._extract_fields(template_str)
        unknown_fields = field_references - set(template_data.keys())
        
        if unknown_fields:
            raise NoNewFactsViolation(
                f"Template references unknown fields: {unknown_fields}"
            )
        
        # Render template
        template = Template(template_str.replace("{", "${"))
        
        # Provide defaults for missing optional fields
        render_data = {k: v if v is not None else "N/A" for k, v in template_data.items()}
        
        try:
            content = template.safe_substitute(render_data)
        except Exception as e:
            content = f"Error generating explanation: {e}"
        
        return Explanation(
            layer=layer,
            content=content.strip(),
            field_references=list(field_references & set(template_data.keys())),
        )
    
    def _extract_fields(self, template_str: str) -> set[str]:
        """Extract field references from template string."""
        import re
        pattern = r"\{(\w+)\}"
        matches = re.findall(pattern, template_str)
        return set(matches)
    
    def _generate_structured(
        self,
        status: str,
        layer: str,
        data: dict[str, Any],
    ) -> Explanation:
        """Generate structured explanation for compliance/deep layers."""
        if layer == "compliance":
            content = self._generate_compliance_view(status, data)
        else:
            content = self._generate_deep_view(status, data)
        
        return Explanation(
            layer=layer,
            content=content,
            field_references=list(self.available_fields),
        )
    
    def _generate_compliance_view(self, status: str, data: dict[str, Any]) -> str:
        """Generate compliance-grade structured view."""
        lines = [
            f"## Compliance Explanation",
            f"",
            f"**Status:** {status.upper()}",
            f"**Snapshot ID:** {data.get('snapshot_id', 'N/A')}",
            f"**Program Version:** {data.get('program_version', 'N/A')}",
            f"**Rules Version:** {data.get('rules_version', 'N/A')}",
            f"",
            f"### Provenance Summary",
        ]
        
        provenance = data.get("provenance", {})
        for field, prov in provenance.items():
            lines.append(f"- {field}: {prov.get('state', 'unknown')} (source: {prov.get('source', 'N/A')})")
        
        lines.extend([
            f"",
            f"### Reason Codes",
        ])
        
        for code in data.get("reason_codes", []):
            lines.append(f"- {code}")
        
        lines.extend([
            f"",
            f"### Audit References",
            f"- Case ID: {data.get('case_id', 'N/A')}",
            f"- Run ID: {data.get('run_id', 'N/A')}",
            f"- Timestamp: {data.get('timestamp', 'N/A')}",
        ])
        
        return "\n".join(lines)
    
    def _generate_deep_view(self, status: str, data: dict[str, Any]) -> str:
        """Generate deep technical view."""
        import json
        
        return json.dumps(
            {
                "status": status,
                "rule_hits": data.get("rule_hits", []),
                "confidence": {
                    "score": data.get("confidence_score", 0),
                    "drivers": data.get("confidence_drivers", []),
                    "caps": data.get("confidence_caps", []),
                },
                "pricing": data.get("pricing", {}),
                "provenance": data.get("provenance", {}),
                "raw_inputs": {k: v for k, v in data.items() if not k.startswith("_")},
            },
            indent=2,
        )
