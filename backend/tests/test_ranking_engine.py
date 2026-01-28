"""
GOATCRD Tests - Ranking Engine
"""
import pytest
from uuid import uuid4

from app.engines.ranking import RankingEngine, RankingMode
from app.engines.scenario_builder import ScenarioResult
from app.models import EligibilityStatus


class TestRankingEngine:
    """Tests for the ranking engine."""
    
    def create_scenario(
        self,
        status: EligibilityStatus,
        confidence: int,
        monthly_payment: float | None = None,
        total_cost: float | None = None,
        verify_count: int = 0,
    ) -> ScenarioResult:
        """Create a test scenario."""
        pricing = None
        if monthly_payment is not None:
            pricing = {
                "monthly_payment": monthly_payment,
                "total_cost": total_cost or monthly_payment * 36,
                "confidence": 80,
            }
        
        return ScenarioResult(
            scenario_id=uuid4(),
            dedup_key="test",
            program_id=uuid4(),
            program_name="Test Program",
            status=status,
            rule_hits=[],
            missing_inputs=[],
            reason_codes=[],
            confidence_score=confidence,
            confidence_drivers=[],
            confidence_caps=[],
            verify_checklist=["item"] * verify_count,
            pricing=pricing,
            pricing_source="estimate" if pricing else "unknown",
        )
    
    def test_lowest_payment_ranking(self):
        """Test lowest payment ranking mode."""
        engine = RankingEngine()
        
        scenarios = [
            self.create_scenario(EligibilityStatus.ELIGIBLE, 80, monthly_payment=500),
            self.create_scenario(EligibilityStatus.ELIGIBLE, 80, monthly_payment=300),
            self.create_scenario(EligibilityStatus.ELIGIBLE, 80, monthly_payment=400),
        ]
        
        result = engine.rank(scenarios, RankingMode.LOWEST_PAYMENT)
        
        # Lowest payment should be rank 1
        assert result.ranked_scenarios[0].scenario.pricing["monthly_payment"] == 300
        assert result.ranked_scenarios[0].rank == 1
    
    def test_highest_certainty_ranking(self):
        """Test highest certainty ranking mode."""
        engine = RankingEngine()
        
        scenarios = [
            self.create_scenario(EligibilityStatus.ELIGIBLE, 60, monthly_payment=300),
            self.create_scenario(EligibilityStatus.ELIGIBLE, 90, monthly_payment=400),
            self.create_scenario(EligibilityStatus.ELIGIBLE, 75, monthly_payment=350),
        ]
        
        result = engine.rank(scenarios, RankingMode.HIGHEST_CERTAINTY)
        
        # Highest confidence should be rank 1
        assert result.ranked_scenarios[0].scenario.confidence_score == 90
        assert result.ranked_scenarios[0].rank == 1
    
    def test_gating_for_low_pricing_confidence(self):
        """Test that low pricing confidence gates scenarios."""
        engine = RankingEngine(pricing_confidence_threshold=50)
        
        # Create scenario with low pricing confidence
        scenario = self.create_scenario(EligibilityStatus.ELIGIBLE, 80)
        scenario.pricing = {"monthly_payment": 300, "confidence": 30}
        
        result = engine.rank([scenario], RankingMode.LOWEST_PAYMENT)
        
        # Should be gated
        assert len(result.gated_scenarios) == 1
        assert len(result.ranked_scenarios) == 0
    
    def test_only_eligible_ranked(self):
        """Test that only ELIGIBLE scenarios are ranked."""
        engine = RankingEngine()
        
        scenarios = [
            self.create_scenario(EligibilityStatus.ELIGIBLE, 80, monthly_payment=300),
            self.create_scenario(EligibilityStatus.REFER, 60),
            self.create_scenario(EligibilityStatus.NOT_ELIGIBLE, 40),
        ]
        
        result = engine.rank(scenarios, RankingMode.HIGHEST_CERTAINTY)
        
        # Only ELIGIBLE should be ranked
        assert len(result.ranked_scenarios) == 1
        assert result.ranked_scenarios[0].scenario.status == EligibilityStatus.ELIGIBLE
    
    def test_sensitivity_notes_for_close_options(self):
        """Test that sensitivity notes are generated for close options."""
        engine = RankingEngine(equivalence_threshold=0.10)
        
        scenarios = [
            self.create_scenario(EligibilityStatus.ELIGIBLE, 80, monthly_payment=300),
            self.create_scenario(EligibilityStatus.ELIGIBLE, 78, monthly_payment=305),
        ]
        
        result = engine.rank(scenarios, RankingMode.LOWEST_PAYMENT)
        
        # Should have sensitivity notes
        assert len(result.sensitivity_notes) > 0
