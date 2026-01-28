"""
GOATCRD Credit Pulse Engine
Real-time credit monitoring and opportunity alerts
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class AlertType(str, Enum):
    """Types of credit pulse alerts."""
    
    SCORE_IMPROVEMENT = "score_improvement"
    SCORE_DROP = "score_drop"
    NEW_OPPORTUNITY = "new_opportunity"
    CLOSING_WINDOW = "closing_window"
    RATE_CHANGE = "rate_change"
    UTILIZATION_WARNING = "utilization_warning"
    PAYMENT_DUE = "payment_due"
    GOAL_PROGRESS = "goal_progress"


class AlertPriority(str, Enum):
    """Alert priority levels."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class CreditSnapshot:
    """Point-in-time credit snapshot."""
    
    snapshot_id: UUID
    consumer_id: UUID
    timestamp: datetime
    
    credit_score: int | None = None
    credit_score_source: str | None = None
    
    total_debt: float | None = None
    total_available_credit: float | None = None
    credit_utilization: float | None = None
    
    open_accounts: int | None = None
    accounts_in_good_standing: int | None = None
    
    recent_inquiries: int | None = None
    oldest_account_age_months: int | None = None


@dataclass
class CreditAlert:
    """Credit pulse alert."""
    
    alert_id: UUID
    consumer_id: UUID
    alert_type: AlertType
    priority: AlertPriority
    
    title: str
    message: str
    action_cta: str | None = None
    
    created_at: datetime = None
    expires_at: datetime | None = None
    dismissed: bool = False
    
    context: dict[str, Any] | None = None


@dataclass
class OpportunityWindow:
    """Time-limited opportunity window."""
    
    window_id: UUID
    consumer_id: UUID
    program_name: str
    
    opened_at: datetime
    closes_at: datetime
    
    eligibility_reason: str
    confidence: int
    
    estimated_savings: float | None = None
    status: str = "open"  # open, actioned, expired


class CreditPulseEngine:
    """
    Real-time credit monitoring and opportunity detection.
    
    Features:
    - Credit score trend analysis
    - Opportunity window detection
    - Proactive alerts for credit events
    - Goal progress tracking
    """
    
    def __init__(self):
        self.thresholds = {
            "score_improvement_min": 10,
            "score_drop_alert": 20,
            "utilization_warning": 0.30,
            "utilization_danger": 0.50,
        }
    
    def analyze_snapshot(
        self,
        current: CreditSnapshot,
        previous: CreditSnapshot | None = None,
    ) -> list[CreditAlert]:
        """
        Analyze credit snapshot and generate alerts.
        
        Compares current snapshot to previous to detect changes.
        """
        alerts = []
        
        if previous and current.credit_score and previous.credit_score:
            score_delta = current.credit_score - previous.credit_score
            
            # Score improvement
            if score_delta >= self.thresholds["score_improvement_min"]:
                alerts.append(CreditAlert(
                    alert_id=uuid4(),
                    consumer_id=current.consumer_id,
                    alert_type=AlertType.SCORE_IMPROVEMENT,
                    priority=AlertPriority.HIGH,
                    title="Your Credit Score Improved!",
                    message=f"Your score increased by {score_delta} points to {current.credit_score}.",
                    action_cta="See new options",
                    created_at=datetime.now(timezone.utc),
                    context={"delta": score_delta, "new_score": current.credit_score},
                ))
            
            # Score drop
            elif score_delta <= -self.thresholds["score_drop_alert"]:
                alerts.append(CreditAlert(
                    alert_id=uuid4(),
                    consumer_id=current.consumer_id,
                    alert_type=AlertType.SCORE_DROP,
                    priority=AlertPriority.URGENT,
                    title="Credit Score Alert",
                    message=f"Your score decreased by {abs(score_delta)} points. Review your report for issues.",
                    action_cta="Review report",
                    created_at=datetime.now(timezone.utc),
                    context={"delta": score_delta, "new_score": current.credit_score},
                ))
        
        # Utilization warning
        if current.credit_utilization:
            if current.credit_utilization >= self.thresholds["utilization_danger"]:
                alerts.append(CreditAlert(
                    alert_id=uuid4(),
                    consumer_id=current.consumer_id,
                    alert_type=AlertType.UTILIZATION_WARNING,
                    priority=AlertPriority.HIGH,
                    title="High Credit Utilization",
                    message=f"Your utilization is {current.credit_utilization * 100:.0f}%. Keeping it under 30% helps your score.",
                    action_cta="See paydown options",
                    created_at=datetime.now(timezone.utc),
                    context={"utilization": current.credit_utilization},
                ))
            elif current.credit_utilization >= self.thresholds["utilization_warning"]:
                alerts.append(CreditAlert(
                    alert_id=uuid4(),
                    consumer_id=current.consumer_id,
                    alert_type=AlertType.UTILIZATION_WARNING,
                    priority=AlertPriority.MEDIUM,
                    title="Credit Utilization Rising",
                    message=f"Your utilization is {current.credit_utilization * 100:.0f}%. Consider paying down balances.",
                    created_at=datetime.now(timezone.utc),
                    context={"utilization": current.credit_utilization},
                ))
        
        return alerts
    
    def detect_opportunities(
        self,
        snapshot: CreditSnapshot,
        current_scenarios: list[dict],
        market_conditions: dict[str, Any] | None = None,
    ) -> list[OpportunityWindow]:
        """
        Detect time-limited opportunity windows.
        
        Analyzes current eligibility + market conditions.
        """
        opportunities = []
        now = datetime.now(timezone.utc)
        
        # Check for newly eligible programs
        for scenario in current_scenarios:
            if scenario.get("status") == "eligible":
                # Check if this is a time-sensitive opportunity
                if self._is_time_sensitive(scenario, market_conditions):
                    opportunities.append(OpportunityWindow(
                        window_id=uuid4(),
                        consumer_id=snapshot.consumer_id,
                        program_name=scenario.get("program_name", "Credit Program"),
                        opened_at=now,
                        closes_at=now + timedelta(days=30),  # Default 30-day window
                        eligibility_reason=self._get_eligibility_reason(scenario),
                        estimated_savings=self._estimate_savings(scenario),
                        confidence=scenario.get("confidence_score", 70),
                    ))
        
        return opportunities
    
    def _is_time_sensitive(
        self,
        scenario: dict,
        market_conditions: dict[str, Any] | None,
    ) -> bool:
        """Check if scenario represents a time-sensitive opportunity."""
        # Promotional rates
        if scenario.get("pricing", {}).get("is_promotional"):
            return True
        
        # Rate environment (if rates are rising, lock in now)
        if market_conditions and market_conditions.get("rate_trend") == "rising":
            return True
        
        # Score threshold edge (close to minimum)
        min_score = scenario.get("min_score", 0)
        current_score = scenario.get("consumer_score", 0)
        if current_score and min_score and (current_score - min_score) < 20:
            return True  # Near the edge
        
        return False
    
    def _get_eligibility_reason(self, scenario: dict) -> str:
        """Generate eligibility reason explanation."""
        reasons = []
        
        if scenario.get("confidence_score", 0) >= 80:
            reasons.append("strong credit profile")
        
        if scenario.get("pricing", {}).get("is_promotional"):
            reasons.append("promotional rate available")
        
        if not reasons:
            reasons.append("meets eligibility requirements")
        
        return "You qualify due to: " + ", ".join(reasons)
    
    def _estimate_savings(self, scenario: dict) -> float | None:
        """Estimate potential savings for a scenario."""
        pricing = scenario.get("pricing")
        if not pricing:
            return None
        
        # Compare to typical rate
        typical_apr = 0.15  # 15% typical
        program_apr = pricing.get("apr", typical_apr)
        loan_amount = pricing.get("amount", 10000)
        
        savings_per_year = (typical_apr - program_apr) * loan_amount
        return round(savings_per_year, 2) if savings_per_year > 0 else None
    
    def generate_goal_alert(
        self,
        consumer_id: UUID,
        goal_name: str,
        current_value: float,
        target_value: float,
        unit: str = "points",
    ) -> CreditAlert | None:
        """
        Generate goal progress alert.
        """
        progress = current_value / target_value if target_value > 0 else 0
        
        if progress >= 1.0:
            return CreditAlert(
                alert_id=uuid4(),
                consumer_id=consumer_id,
                alert_type=AlertType.GOAL_PROGRESS,
                priority=AlertPriority.HIGH,
                title="Goal Achieved! 🎉",
                message=f"You've reached your {goal_name} goal!",
                action_cta="See new options",
                created_at=datetime.now(timezone.utc),
                context={"goal": goal_name, "value": current_value, "target": target_value},
            )
        elif progress >= 0.9:
            remaining = target_value - current_value
            return CreditAlert(
                alert_id=uuid4(),
                consumer_id=consumer_id,
                alert_type=AlertType.GOAL_PROGRESS,
                priority=AlertPriority.MEDIUM,
                title="Almost There!",
                message=f"You're {remaining:.0f} {unit} away from your {goal_name} goal.",
                created_at=datetime.now(timezone.utc),
                context={"goal": goal_name, "progress": progress},
            )
        
        return None
    
    def calculate_trend(
        self,
        snapshots: list[CreditSnapshot],
        field: str = "credit_score",
    ) -> dict[str, Any]:
        """
        Calculate trend from historical snapshots.
        """
        if len(snapshots) < 2:
            return {"trend": "insufficient_data", "points": []}
        
        values = [getattr(s, field, None) for s in snapshots if getattr(s, field, None) is not None]
        
        if len(values) < 2:
            return {"trend": "insufficient_data", "points": []}
        
        # Simple trend detection
        first_half_avg = sum(values[:len(values)//2]) / (len(values)//2)
        second_half_avg = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        
        delta = second_half_avg - first_half_avg
        
        if delta > 5:
            trend = "improving"
        elif delta < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "delta": delta,
            "current": values[-1],
            "previous": values[0],
            "points": [
                {"timestamp": s.timestamp.isoformat(), "value": getattr(s, field)}
                for s in snapshots
                if getattr(s, field, None) is not None
            ],
        }


# Singleton instance
credit_pulse_engine = CreditPulseEngine()
