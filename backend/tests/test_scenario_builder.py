"""
GOATCRD Tests - Scenario Builder Engine
"""
import pytest
from uuid import uuid4

from app.engines.scenario_builder import ScenarioBuilder, EXAMPLE_PROGRAM_CATALOG
from app.engines.confidence import ConfidenceEngine
from app.models import EligibilityStatus


class TestScenarioBuilder:
    """Tests for the scenario builder engine."""
    
    def test_build_eligible_scenarios(self):
        """Test that eligible scenarios are correctly identified."""
        builder = ScenarioBuilder(EXAMPLE_PROGRAM_CATALOG)
        
        intake_data = {
            "annual_income": 75000,
            "dti_ratio": 0.25,
            "credit_score": 750,
            "loan_amount": 15000,
            "term_months": 36,
        }
        
        provenance = {
            "annual_income": {"state": "verified", "source": "payroll"},
            "credit_score": {"state": "verified", "source": "bureau"},
        }
        
        result = builder.build(
            intake_data=intake_data,
            provenance=provenance,
            intake_snapshot_id=uuid4(),
        )
        
        assert result.total_scenarios > 0
        assert len(result.eligible) > 0
    
    def test_build_not_eligible_scenarios(self):
        """Test that not-eligible scenarios are correctly identified."""
        builder = ScenarioBuilder(EXAMPLE_PROGRAM_CATALOG)
        
        intake_data = {
            "annual_income": 20000,  # Too low for most programs
            "dti_ratio": 0.25,
            "credit_score": 550,  # Too low
        }
        
        provenance = {}
        
        result = builder.build(
            intake_data=intake_data,
            provenance=provenance,
            intake_snapshot_id=uuid4(),
        )
        
        # All scenarios should be not-eligible or refer
        assert len(result.eligible) == 0
    
    def test_dedup_key_determinism(self):
        """Test that dedup keys are deterministic."""
        builder = ScenarioBuilder(EXAMPLE_PROGRAM_CATALOG)
        
        intake_data = {
            "annual_income": 60000,
            "dti_ratio": 0.30,
            "credit_score": 700,
        }
        
        result1 = builder.build(
            intake_data=intake_data,
            provenance={},
            intake_snapshot_id=uuid4(),
        )
        
        result2 = builder.build(
            intake_data=intake_data,
            provenance={},
            intake_snapshot_id=uuid4(),
        )
        
        # Same input should produce same dedup keys
        keys1 = {s.dedup_key for s in result1.eligible + result1.refer + result1.not_eligible}
        keys2 = {s.dedup_key for s in result2.eligible + result2.refer + result2.not_eligible}
        
        assert keys1 == keys2
    
    def test_pricing_calculation(self):
        """Test that pricing is calculated for eligible scenarios."""
        builder = ScenarioBuilder(EXAMPLE_PROGRAM_CATALOG)
        
        intake_data = {
            "annual_income": 100000,
            "dti_ratio": 0.20,
            "credit_score": 800,
            "loan_amount": 10000,
            "term_months": 24,
        }
        
        result = builder.build(
            intake_data=intake_data,
            provenance={},
            intake_snapshot_id=uuid4(),
        )
        
        # Eligible scenarios should have pricing
        for scenario in result.eligible:
            assert scenario.pricing is not None
            assert "monthly_payment" in scenario.pricing
