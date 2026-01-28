"""
Tests for GOATCRD Credit Pulse Engine
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.engines.credit_pulse import (
    CreditPulseEngine,
    CreditSnapshot,
    CreditAlert,
    AlertType,
    AlertPriority,
)


class TestCreditPulseEngine:
    """Test suite for CreditPulseEngine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = CreditPulseEngine()
        self.consumer_id = uuid4()
    
    def _create_snapshot(
        self,
        credit_score: int | None = 720,
        utilization: float | None = 0.25,
    ) -> CreditSnapshot:
        """Helper to create test snapshots."""
        return CreditSnapshot(
            snapshot_id=uuid4(),
            consumer_id=self.consumer_id,
            timestamp=datetime.now(timezone.utc),
            credit_score=credit_score,
            credit_score_source="equifax",
            credit_utilization=utilization,
            total_debt=15000,
            total_available_credit=60000,
        )
    
    def test_analyze_snapshot_detects_score_improvement(self):
        """Test that score improvement is detected."""
        previous = self._create_snapshot(credit_score=700)
        current = self._create_snapshot(credit_score=720)
        
        alerts = self.engine.analyze_snapshot(current, previous)
        
        score_alerts = [a for a in alerts if a.alert_type == AlertType.SCORE_IMPROVEMENT]
        assert len(score_alerts) == 1
        assert score_alerts[0].priority == AlertPriority.HIGH
    
    def test_analyze_snapshot_detects_score_drop(self):
        """Test that significant score drop is detected."""
        previous = self._create_snapshot(credit_score=720)
        current = self._create_snapshot(credit_score=695)
        
        alerts = self.engine.analyze_snapshot(current, previous)
        
        drop_alerts = [a for a in alerts if a.alert_type == AlertType.SCORE_DROP]
        assert len(drop_alerts) == 1
        assert drop_alerts[0].priority == AlertPriority.URGENT
    
    def test_analyze_snapshot_warns_high_utilization(self):
        """Test that high utilization triggers warning."""
        current = self._create_snapshot(utilization=0.55)
        
        alerts = self.engine.analyze_snapshot(current)
        
        util_alerts = [a for a in alerts if a.alert_type == AlertType.UTILIZATION_WARNING]
        assert len(util_alerts) == 1
        assert util_alerts[0].priority == AlertPriority.HIGH
    
    def test_analyze_snapshot_warns_moderate_utilization(self):
        """Test that moderate utilization triggers medium warning."""
        current = self._create_snapshot(utilization=0.35)
        
        alerts = self.engine.analyze_snapshot(current)
        
        util_alerts = [a for a in alerts if a.alert_type == AlertType.UTILIZATION_WARNING]
        assert len(util_alerts) == 1
        assert util_alerts[0].priority == AlertPriority.MEDIUM
    
    def test_analyze_snapshot_no_alert_for_good_utilization(self):
        """Test that good utilization doesn't trigger warning."""
        current = self._create_snapshot(utilization=0.15)
        
        alerts = self.engine.analyze_snapshot(current)
        
        util_alerts = [a for a in alerts if a.alert_type == AlertType.UTILIZATION_WARNING]
        assert len(util_alerts) == 0
    
    def test_detect_opportunities_finds_eligible_programs(self):
        """Test that opportunities are detected for eligible programs."""
        snapshot = self._create_snapshot(credit_score=750)
        
        scenarios = [
            {
                "program_name": "Prime Loan",
                "status": "eligible",
                "confidence_score": 85,
                "pricing": {"is_promotional": True, "apr": 0.08},
            },
        ]
        
        # Market conditions suggesting rates are rising
        market = {"rate_trend": "rising"}
        
        opportunities = self.engine.detect_opportunities(
            snapshot, scenarios, market
        )
        
        assert len(opportunities) >= 1
        assert opportunities[0].program_name == "Prime Loan"
    
    def test_generate_goal_alert_goal_achieved(self):
        """Test goal progress alert when goal is achieved."""
        alert = self.engine.generate_goal_alert(
            consumer_id=self.consumer_id,
            goal_name="Credit Score Target",
            current_value=750,
            target_value=740,
        )
        
        assert alert is not None
        assert alert.alert_type == AlertType.GOAL_PROGRESS
        assert "Achieved" in alert.title
    
    def test_generate_goal_alert_almost_there(self):
        """Test goal progress alert when close to goal."""
        alert = self.engine.generate_goal_alert(
            consumer_id=self.consumer_id,
            goal_name="Credit Score Target",
            current_value=735,
            target_value=740,
        )
        
        assert alert is not None
        assert "Almost" in alert.title
    
    def test_generate_goal_alert_no_alert_when_far(self):
        """Test no alert when far from goal."""
        alert = self.engine.generate_goal_alert(
            consumer_id=self.consumer_id,
            goal_name="Credit Score Target",
            current_value=650,
            target_value=740,
        )
        
        assert alert is None
    
    def test_calculate_trend_improving(self):
        """Test trend calculation for improving scores."""
        snapshots = [
            self._create_snapshot(credit_score=680),
            self._create_snapshot(credit_score=690),
            self._create_snapshot(credit_score=700),
            self._create_snapshot(credit_score=715),
        ]
        
        result = self.engine.calculate_trend(snapshots)
        
        assert result["trend"] == "improving"
        assert result["delta"] > 0
    
    def test_calculate_trend_declining(self):
        """Test trend calculation for declining scores."""
        snapshots = [
            self._create_snapshot(credit_score=720),
            self._create_snapshot(credit_score=710),
            self._create_snapshot(credit_score=695),
            self._create_snapshot(credit_score=680),
        ]
        
        result = self.engine.calculate_trend(snapshots)
        
        assert result["trend"] == "declining"
        assert result["delta"] < 0
    
    def test_calculate_trend_stable(self):
        """Test trend calculation for stable scores."""
        snapshots = [
            self._create_snapshot(credit_score=700),
            self._create_snapshot(credit_score=702),
            self._create_snapshot(credit_score=699),
            self._create_snapshot(credit_score=701),
        ]
        
        result = self.engine.calculate_trend(snapshots)
        
        assert result["trend"] == "stable"
    
    def test_calculate_trend_insufficient_data(self):
        """Test trend with insufficient data."""
        snapshots = [self._create_snapshot()]
        
        result = self.engine.calculate_trend(snapshots)
        
        assert result["trend"] == "insufficient_data"
