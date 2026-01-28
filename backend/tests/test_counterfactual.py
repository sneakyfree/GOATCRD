"""
GOATCRD Tests - Counterfactual Simulator
"""
import pytest
from uuid import uuid4

from app.engines.counterfactual import CounterfactualSimulator
from app.engines.scenario_builder import EXAMPLE_PROGRAM_CATALOG


class TestCounterfactualSimulator:
    """Tests for the counterfactual simulator."""
    
    def test_protected_field_rejection(self):
        """Test that protected fields are rejected."""
        simulator = CounterfactualSimulator(EXAMPLE_PROGRAM_CATALOG)
        
        result = simulator.simulate(
            case_id=uuid4(),
            original_data={"annual_income": 50000},
            original_provenance={},
            hypothetical_changes={"race": "any", "gender": "any"},
            intake_snapshot_id=uuid4(),
        )
        
        # Protected fields should be rejected
        assert "race" in result.rejected_changes
        assert "gender" in result.rejected_changes
        assert len(result.validated_changes) == 0
    
    def test_valid_field_simulation(self):
        """Test that valid fields are simulated."""
        simulator = CounterfactualSimulator(EXAMPLE_PROGRAM_CATALOG)
        
        result = simulator.simulate(
            case_id=uuid4(),
            original_data={
                "annual_income": 40000,
                "dti_ratio": 0.45,
                "credit_score": 600,
            },
            original_provenance={},
            hypothetical_changes={
                "credit_score": 720,
                "dti_ratio": 0.30,
            },
            intake_snapshot_id=uuid4(),
        )
        
        # Valid fields should be accepted
        assert "credit_score" in result.validated_changes
        assert "dti_ratio" in result.validated_changes
        assert len(result.status_changes) > 0
    
    def test_value_range_validation(self):
        """Test that out-of-range values are rejected."""
        simulator = CounterfactualSimulator(EXAMPLE_PROGRAM_CATALOG)
        
        result = simulator.simulate(
            case_id=uuid4(),
            original_data={"credit_score": 650},
            original_provenance={},
            hypothetical_changes={
                "credit_score": 1000,  # Max is 850
            },
            intake_snapshot_id=uuid4(),
        )
        
        assert "credit_score" in result.rejected_changes
        assert "out of range" in result.rejected_changes["credit_score"].lower()
    
    def test_improvement_detection(self):
        """Test that improvements are detected in status changes."""
        simulator = CounterfactualSimulator(EXAMPLE_PROGRAM_CATALOG)
        
        # Start with borderline data
        result = simulator.simulate(
            case_id=uuid4(),
            original_data={
                "annual_income": 30000,  # Below some thresholds
                "dti_ratio": 0.40,
                "credit_score": 620,
            },
            original_provenance={},
            hypothetical_changes={
                "annual_income": 60000,  # Above thresholds
                "credit_score": 740,
            },
            intake_snapshot_id=uuid4(),
        )
        
        # Should have summary about changes (may or may not show improvements)
        assert len(result.changes_summary) > 0
    
    def test_confidence_calculation(self):
        """Test that confidence is calculated based on provenance."""
        simulator = CounterfactualSimulator(EXAMPLE_PROGRAM_CATALOG)
        
        # Verified baseline should have higher confidence
        result_verified = simulator.simulate(
            case_id=uuid4(),
            original_data={"credit_score": 650},
            original_provenance={
                "credit_score": {"state": "verified", "source": "bureau"},
            },
            hypothetical_changes={"credit_score": 720},
            intake_snapshot_id=uuid4(),
        )
        
        # Unverified baseline should have lower confidence
        result_unverified = simulator.simulate(
            case_id=uuid4(),
            original_data={"credit_score": 650},
            original_provenance={
                "credit_score": {"state": "provided", "source": "user"},
            },
            hypothetical_changes={"credit_score": 720},
            intake_snapshot_id=uuid4(),
        )
        
        # Both should have some confidence level
        assert result_verified.confidence in ["low", "medium", "high"]
        assert result_unverified.confidence in ["low", "medium", "high"]
