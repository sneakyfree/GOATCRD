"""
Delta Report Service
S4.3 - Generate version comparison and impact reports
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from enum import Enum


class ChangeImpact(str, Enum):
    """Impact level of a change."""
    BREAKING = "breaking"  # May change eligibility decisions
    MAJOR = "major"        # Significant rule changes
    MINOR = "minor"        # Small adjustments
    PATCH = "patch"        # Documentation/metadata only


class ChangeType(str, Enum):
    """Type of change between versions."""
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    THRESHOLD_CHANGE = "threshold_change"
    LOGIC_CHANGE = "logic_change"


@dataclass
class VersionChange:
    """Represents a single change between versions."""
    
    change_id: UUID
    field: str
    change_type: ChangeType
    old_value: Any
    new_value: Any
    impact: ChangeImpact
    description: str


@dataclass
class DeltaReport:
    """Version comparison report."""
    
    report_id: UUID
    program_id: UUID
    from_version: str
    to_version: str
    
    # Changes
    changes: list[VersionChange]
    overall_impact: ChangeImpact
    
    # Impact analysis
    affected_scenarios_estimate: int
    breaking_changes_count: int
    
    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    generated_by: str = "system"


class DeltaReportService:
    """
    Generates version comparison reports.
    
    Analyzes differences between program versions and
    estimates impact on existing decisions.
    """
    
    def __init__(self):
        self.reports: dict[UUID, DeltaReport] = {}
    
    def generate_delta_report(
        self,
        program_id: UUID,
        from_version: dict[str, Any],
        to_version: dict[str, Any],
        from_version_str: str,
        to_version_str: str,
    ) -> DeltaReport:
        """Generate a delta report between two versions."""
        
        changes = []
        
        # Compare rules
        rule_changes = self._compare_rules(
            from_version.get("rules", []),
            to_version.get("rules", []),
        )
        changes.extend(rule_changes)
        
        # Compare thresholds
        threshold_changes = self._compare_thresholds(
            from_version.get("thresholds", {}),
            to_version.get("thresholds", {}),
        )
        changes.extend(threshold_changes)
        
        # Determine overall impact
        breaking_count = sum(1 for c in changes if c.impact == ChangeImpact.BREAKING)
        major_count = sum(1 for c in changes if c.impact == ChangeImpact.MAJOR)
        
        if breaking_count > 0:
            overall_impact = ChangeImpact.BREAKING
        elif major_count > 0:
            overall_impact = ChangeImpact.MAJOR
        elif len(changes) > 0:
            overall_impact = ChangeImpact.MINOR
        else:
            overall_impact = ChangeImpact.PATCH
        
        # Estimate affected scenarios
        affected_estimate = self._estimate_affected_scenarios(changes)
        
        report = DeltaReport(
            report_id=uuid4(),
            program_id=program_id,
            from_version=from_version_str,
            to_version=to_version_str,
            changes=changes,
            overall_impact=overall_impact,
            affected_scenarios_estimate=affected_estimate,
            breaking_changes_count=breaking_count,
        )
        
        self.reports[report.report_id] = report
        return report
    
    def _compare_rules(
        self,
        old_rules: list[dict],
        new_rules: list[dict],
    ) -> list[VersionChange]:
        """Compare rule sets and identify changes."""
        changes = []
        
        old_by_id = {r.get("id", r.get("name")): r for r in old_rules}
        new_by_id = {r.get("id", r.get("name")): r for r in new_rules}
        
        # Find removed rules
        for rule_id in old_by_id:
            if rule_id not in new_by_id:
                changes.append(VersionChange(
                    change_id=uuid4(),
                    field=f"rules.{rule_id}",
                    change_type=ChangeType.REMOVED,
                    old_value=old_by_id[rule_id],
                    new_value=None,
                    impact=ChangeImpact.BREAKING,
                    description=f"Rule '{rule_id}' was removed",
                ))
        
        # Find added rules
        for rule_id in new_by_id:
            if rule_id not in old_by_id:
                changes.append(VersionChange(
                    change_id=uuid4(),
                    field=f"rules.{rule_id}",
                    change_type=ChangeType.ADDED,
                    old_value=None,
                    new_value=new_by_id[rule_id],
                    impact=ChangeImpact.MAJOR,
                    description=f"Rule '{rule_id}' was added",
                ))
        
        # Find modified rules
        for rule_id in old_by_id:
            if rule_id in new_by_id:
                old_rule = old_by_id[rule_id]
                new_rule = new_by_id[rule_id]
                
                if old_rule != new_rule:
                    # Determine impact based on what changed
                    impact = self._determine_rule_change_impact(old_rule, new_rule)
                    
                    changes.append(VersionChange(
                        change_id=uuid4(),
                        field=f"rules.{rule_id}",
                        change_type=ChangeType.MODIFIED,
                        old_value=old_rule,
                        new_value=new_rule,
                        impact=impact,
                        description=f"Rule '{rule_id}' was modified",
                    ))
        
        return changes
    
    def _compare_thresholds(
        self,
        old_thresholds: dict,
        new_thresholds: dict,
    ) -> list[VersionChange]:
        """Compare thresholds and identify changes."""
        changes = []
        
        all_keys = set(old_thresholds.keys()) | set(new_thresholds.keys())
        
        for key in all_keys:
            old_val = old_thresholds.get(key)
            new_val = new_thresholds.get(key)
            
            if old_val != new_val:
                if old_val is None:
                    change_type = ChangeType.ADDED
                    impact = ChangeImpact.MAJOR
                    desc = f"Threshold '{key}' was added with value {new_val}"
                elif new_val is None:
                    change_type = ChangeType.REMOVED
                    impact = ChangeImpact.BREAKING
                    desc = f"Threshold '{key}' was removed"
                else:
                    change_type = ChangeType.THRESHOLD_CHANGE
                    impact = self._determine_threshold_impact(key, old_val, new_val)
                    desc = f"Threshold '{key}' changed from {old_val} to {new_val}"
                
                changes.append(VersionChange(
                    change_id=uuid4(),
                    field=f"thresholds.{key}",
                    change_type=change_type,
                    old_value=old_val,
                    new_value=new_val,
                    impact=impact,
                    description=desc,
                ))
        
        return changes
    
    def _determine_rule_change_impact(
        self,
        old_rule: dict,
        new_rule: dict,
    ) -> ChangeImpact:
        """Determine impact of a rule change."""
        # Check if core logic changed
        old_condition = old_rule.get("condition", old_rule.get("logic"))
        new_condition = new_rule.get("condition", new_rule.get("logic"))
        
        if old_condition != new_condition:
            return ChangeImpact.BREAKING
        
        # Check if thresholds within rule changed
        old_thresh = old_rule.get("threshold", old_rule.get("value"))
        new_thresh = new_rule.get("threshold", new_rule.get("value"))
        
        if old_thresh != new_thresh:
            return ChangeImpact.MAJOR
        
        return ChangeImpact.MINOR
    
    def _determine_threshold_impact(
        self,
        key: str,
        old_val: Any,
        new_val: Any,
    ) -> ChangeImpact:
        """Determine impact of a threshold change."""
        critical_thresholds = [
            "min_credit_score",
            "max_dti",
            "min_income",
            "max_ltv",
        ]
        
        if key in critical_thresholds:
            if isinstance(old_val, (int, float)) and isinstance(new_val, (int, float)):
                change_pct = abs(new_val - old_val) / max(abs(old_val), 1) * 100
                if change_pct > 10:
                    return ChangeImpact.BREAKING
                elif change_pct > 5:
                    return ChangeImpact.MAJOR
        
        return ChangeImpact.MINOR
    
    def _estimate_affected_scenarios(self, changes: list[VersionChange]) -> int:
        """Estimate number of scenarios affected by changes."""
        # This would query historical data in production
        # For now, use heuristic based on change impact
        
        base_estimate = 0
        for change in changes:
            if change.impact == ChangeImpact.BREAKING:
                base_estimate += 500
            elif change.impact == ChangeImpact.MAJOR:
                base_estimate += 100
            elif change.impact == ChangeImpact.MINOR:
                base_estimate += 20
        
        return min(base_estimate, 10000)  # Cap at 10k
    
    def get_report(self, report_id: UUID) -> DeltaReport | None:
        """Get a delta report by ID."""
        return self.reports.get(report_id)
    
    def export_report(self, report_id: UUID) -> dict[str, Any] | None:
        """Export a delta report as JSON."""
        report = self.get_report(report_id)
        if not report:
            return None
        
        return {
            "report_id": str(report.report_id),
            "program_id": str(report.program_id),
            "from_version": report.from_version,
            "to_version": report.to_version,
            "overall_impact": report.overall_impact.value,
            "affected_scenarios_estimate": report.affected_scenarios_estimate,
            "breaking_changes_count": report.breaking_changes_count,
            "changes": [
                {
                    "field": c.field,
                    "change_type": c.change_type.value,
                    "impact": c.impact.value,
                    "description": c.description,
                    "old_value": c.old_value,
                    "new_value": c.new_value,
                }
                for c in report.changes
            ],
            "generated_at": report.generated_at.isoformat(),
        }


# Singleton instance
delta_service = DeltaReportService()
