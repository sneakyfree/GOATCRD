"""
GOATCRD Tests - Rules Engine
"""
import pytest

from app.engines.rules import RulesEngine, DEFAULT_PERSONAL_LOAN_RULESET
from app.models import EligibilityStatus


class TestRulesEngine:
    """Tests for the rules engine."""
    
    def test_eligible_scenario(self):
        """Test that valid data returns ELIGIBLE status."""
        engine = RulesEngine(DEFAULT_PERSONAL_LOAN_RULESET)
        
        data = {
            "annual_income": 60000,
            "dti_ratio": 0.30,
            "credit_score": 720,
            "bankruptcy_months": 120,
        }
        
        result = engine.evaluate(data)
        
        assert result.status == EligibilityStatus.ELIGIBLE
        assert len(result.reason_codes) == 0
        assert len(result.missing_inputs) == 0
    
    def test_not_eligible_low_income(self):
        """Test that low income returns NOT_ELIGIBLE with reason code."""
        engine = RulesEngine(DEFAULT_PERSONAL_LOAN_RULESET)
        
        data = {
            "annual_income": 20000,  # Below threshold
            "dti_ratio": 0.30,
            "credit_score": 720,
            "bankruptcy_months": 120,
        }
        
        result = engine.evaluate(data)
        
        assert result.status == EligibilityStatus.NOT_ELIGIBLE
        assert "RC004" in result.reason_codes
    
    def test_not_eligible_high_dti(self):
        """Test that high DTI returns NOT_ELIGIBLE with reason code."""
        engine = RulesEngine(DEFAULT_PERSONAL_LOAN_RULESET)
        
        data = {
            "annual_income": 60000,
            "dti_ratio": 0.50,  # Above threshold
            "credit_score": 720,
            "bankruptcy_months": 120,
        }
        
        result = engine.evaluate(data)
        
        assert result.status == EligibilityStatus.NOT_ELIGIBLE
        assert "RC003" in result.reason_codes
    
    def test_refer_missing_fields(self):
        """Test that missing fields return REFER status."""
        engine = RulesEngine(DEFAULT_PERSONAL_LOAN_RULESET)
        
        data = {
            "annual_income": 60000,
            "dti_ratio": 0.30,
            # Missing: credit_score, bankruptcy_months
        }
        
        result = engine.evaluate(data)
        
        assert result.status == EligibilityStatus.REFER
        assert "credit_score" in result.missing_inputs
        assert "bankruptcy_months" in result.missing_inputs
    
    def test_recent_bankruptcy(self):
        """Test that recent bankruptcy returns NOT_ELIGIBLE."""
        engine = RulesEngine(DEFAULT_PERSONAL_LOAN_RULESET)
        
        data = {
            "annual_income": 60000,
            "dti_ratio": 0.30,
            "credit_score": 720,
            "bankruptcy_months": 24,  # Within 48 months
        }
        
        result = engine.evaluate(data)
        
        assert result.status == EligibilityStatus.NOT_ELIGIBLE
        assert "RC007" in result.reason_codes
    
    def test_multiple_failures(self):
        """Test that multiple failures return all reason codes."""
        engine = RulesEngine(DEFAULT_PERSONAL_LOAN_RULESET)
        
        data = {
            "annual_income": 15000,  # Fail
            "dti_ratio": 0.60,  # Fail
            "credit_score": 500,  # Fail
            "bankruptcy_months": 12,  # Fail
        }
        
        result = engine.evaluate(data)
        
        assert result.status == EligibilityStatus.NOT_ELIGIBLE
        assert len(result.reason_codes) >= 3
