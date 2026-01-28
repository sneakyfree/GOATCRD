"""
GOATCRD Export Engine
Generates PDF, JSON, and structured exports
"""
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID


@dataclass
class ExportContent:
    """Exported content ready for delivery."""
    
    export_type: str
    format: str
    filename: str
    content: str | bytes
    metadata: dict[str, Any]


class ExportEngine:
    """
    Generates compliant exports for scenarios and cases.
    
    Supports:
    - JSON structured export
    - PDF summary (via template)
    - CSV data export
    """
    
    def __init__(self, app_version: str = "0.1.0"):
        self.app_version = app_version
    
    def export_scenario_summary(
        self,
        case_id: UUID,
        scenarios: list[dict],
        rankings: dict[str, Any] | None = None,
        format: str = "json",
    ) -> ExportContent:
        """
        Export scenario summary.
        
        Args:
            case_id: Case ID
            scenarios: List of scenario dicts
            rankings: Optional rankings data
            format: Export format (json, pdf, csv)
        
        Returns:
            ExportContent ready for delivery
        """
        timestamp = datetime.now(timezone.utc)
        
        if format == "json":
            return self._export_json(case_id, scenarios, rankings, timestamp)
        elif format == "pdf":
            return self._export_pdf(case_id, scenarios, rankings, timestamp)
        elif format == "csv":
            return self._export_csv(case_id, scenarios, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(
        self,
        case_id: UUID,
        scenarios: list[dict],
        rankings: dict[str, Any] | None,
        timestamp: datetime,
    ) -> ExportContent:
        """Generate JSON export."""
        
        export_data = {
            "export_type": "scenario_summary",
            "case_id": str(case_id),
            "generated_at": timestamp.isoformat(),
            "app_version": self.app_version,
            "scenarios": {
                "total": len(scenarios),
                "eligible": [s for s in scenarios if s.get("status") == "eligible"],
                "refer": [s for s in scenarios if s.get("status") == "refer"],
                "not_eligible": [s for s in scenarios if s.get("status") == "not_eligible"],
            },
            "rankings": rankings,
            "disclaimer": (
                "This is an estimate based on the information provided. "
                "Actual eligibility depends on verification and current program terms."
            ),
        }
        
        content = json.dumps(export_data, indent=2, default=str)
        
        return ExportContent(
            export_type="scenario_summary",
            format="json",
            filename=f"goatcrd_scenarios_{case_id}_{timestamp.strftime('%Y%m%d')}.json",
            content=content,
            metadata={
                "case_id": str(case_id),
                "generated_at": timestamp.isoformat(),
                "scenario_count": len(scenarios),
            },
        )
    
    def _export_pdf(
        self,
        case_id: UUID,
        scenarios: list[dict],
        rankings: dict[str, Any] | None,
        timestamp: datetime,
    ) -> ExportContent:
        """Generate PDF export (HTML template for WeasyPrint)."""
        
        # Generate HTML that can be converted to PDF
        eligible = [s for s in scenarios if s.get("status") == "eligible"]
        refer = [s for s in scenarios if s.get("status") == "refer"]
        not_eligible = [s for s in scenarios if s.get("status") == "not_eligible"]
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>GOATCRD Scenario Summary</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; margin: 40px; color: #1a1a1a; }}
        h1 {{ color: #0369a1; }}
        h2 {{ color: #0c4a6e; border-bottom: 2px solid #0ea5e9; padding-bottom: 8px; }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ flex: 1; padding: 20px; border-radius: 8px; text-align: center; }}
        .eligible {{ background: #dcfce7; color: #166534; }}
        .refer {{ background: #fef9c3; color: #854d0e; }}
        .not-eligible {{ background: #fee2e2; color: #991b1b; }}
        .scenario {{ margin-bottom: 20px; padding: 15px; border: 1px solid #e5e7eb; border-radius: 8px; }}
        .scenario-header {{ display: flex; justify-content: space-between; }}
        .confidence {{ font-size: 0.9em; color: #666; }}
        .pricing {{ font-size: 1.2em; font-weight: bold; color: #0369a1; }}
        .disclaimer {{ margin-top: 40px; padding: 20px; background: #f3f4f6; border-radius: 8px; font-size: 0.9em; color: #666; }}
        .footer {{ margin-top: 40px; text-align: center; color: #999; font-size: 0.8em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>GOATCRD Scenario Summary</h1>
        <p>Generated: {timestamp.strftime('%B %d, %Y at %I:%M %p')}</p>
        <p>Case ID: {str(case_id)[:8]}...</p>
    </div>
    
    <div class="summary">
        <div class="summary-card eligible">
            <h3>{len(eligible)}</h3>
            <p>Eligible</p>
        </div>
        <div class="summary-card refer">
            <h3>{len(refer)}</h3>
            <p>Need Info</p>
        </div>
        <div class="summary-card not-eligible">
            <h3>{len(not_eligible)}</h3>
            <p>Not Eligible</p>
        </div>
    </div>
    
    <h2>Eligible Options</h2>
    {"".join(self._render_scenario_html(s) for s in eligible) or "<p>No eligible options found.</p>"}
    
    <h2>More Information Needed</h2>
    {"".join(self._render_scenario_html(s) for s in refer) or "<p>None.</p>"}
    
    <div class="disclaimer">
        <strong>Important:</strong> This is an estimate based on the information provided. 
        Actual eligibility depends on verification and current program terms. 
        This is not an approval or guarantee of any terms.
    </div>
    
    <div class="footer">
        <p>GOATCRD v{self.app_version} • Compliance-First Credit Intelligence</p>
    </div>
</body>
</html>
"""
        
        return ExportContent(
            export_type="scenario_summary",
            format="pdf",
            filename=f"goatcrd_scenarios_{case_id}_{timestamp.strftime('%Y%m%d')}.html",
            content=html_content,
            metadata={
                "case_id": str(case_id),
                "generated_at": timestamp.isoformat(),
                "scenario_count": len(scenarios),
                "note": "HTML template for PDF conversion via WeasyPrint",
            },
        )
    
    def _render_scenario_html(self, scenario: dict) -> str:
        """Render a single scenario as HTML."""
        pricing = scenario.get("pricing", {})
        monthly = pricing.get("monthly_payment", "N/A")
        confidence = scenario.get("confidence_score", "N/A")
        
        return f"""
        <div class="scenario">
            <div class="scenario-header">
                <h4>{scenario.get('program_name', 'Program')}</h4>
                <span class="pricing">${monthly}/mo</span>
            </div>
            <p class="confidence">Confidence: {confidence}%</p>
        </div>
        """
    
    def _export_csv(
        self,
        case_id: UUID,
        scenarios: list[dict],
        timestamp: datetime,
    ) -> ExportContent:
        """Generate CSV export."""
        
        headers = [
            "program_name",
            "status",
            "confidence_score",
            "monthly_payment",
            "total_cost",
            "reason_codes",
        ]
        
        rows = [",".join(headers)]
        
        for s in scenarios:
            pricing = s.get("pricing", {})
            row = [
                s.get("program_name", ""),
                s.get("status", ""),
                str(s.get("confidence_score", "")),
                str(pricing.get("monthly_payment", "")),
                str(pricing.get("total_cost", "")),
                ";".join(s.get("reason_codes", [])),
            ]
            rows.append(",".join(f'"{v}"' for v in row))
        
        content = "\n".join(rows)
        
        return ExportContent(
            export_type="scenario_summary",
            format="csv",
            filename=f"goatcrd_scenarios_{case_id}_{timestamp.strftime('%Y%m%d')}.csv",
            content=content,
            metadata={
                "case_id": str(case_id),
                "generated_at": timestamp.isoformat(),
                "scenario_count": len(scenarios),
            },
        )
    
    def export_consumer_data(
        self,
        consumer_id: UUID,
        data: dict[str, Any],
        format: str = "json",
    ) -> ExportContent:
        """
        Export consumer's data for 1033 compliance.
        """
        timestamp = datetime.now(timezone.utc)
        
        export_data = {
            "export_type": "consumer_data",
            "consumer_id": str(consumer_id),
            "generated_at": timestamp.isoformat(),
            "data": data,
            "rights_notice": (
                "Under Section 1033 of the Consumer Financial Protection Act, "
                "you have the right to access your financial data. This export "
                "contains all data we hold about you."
            ),
        }
        
        content = json.dumps(export_data, indent=2, default=str)
        
        return ExportContent(
            export_type="consumer_data",
            format="json",
            filename=f"goatcrd_my_data_{timestamp.strftime('%Y%m%d')}.json",
            content=content,
            metadata={
                "consumer_id": str(consumer_id),
                "generated_at": timestamp.isoformat(),
            },
        )


# Singleton instance
export_engine = ExportEngine()
