"""
GOATCRD Tests - Confidence Engine
"""
import pytest

from app.engines.confidence import ConfidenceEngine
from app.schemas.base import ProvenanceState


class TestConfidenceEngine:
    """Tests for the confidence engine."""
    
    def test_full_confidence_verified(self):
        """Test that fully verified data gets high confidence."""
        engine = ConfidenceEngine()
        
        provenance = {
            "income": {"state": ProvenanceState.VERIFIED, "source": "payroll_api"},
            "credit_score": {"state": ProvenanceState.VERIFIED, "source": "bureau"},
        }
        
        result = engine.calculate(provenance)
        
        assert result.score == 100
        assert len(result.caps_applied) == 0
    
    def test_unknown_caps_confidence(self):
        """Test that unknown fields cap confidence."""
        engine = ConfidenceEngine(unknown_cap=50)
        
        provenance = {
            "income": {"state": ProvenanceState.VERIFIED, "source": "payroll_api"},
            "credit_score": {"state": ProvenanceState.UNKNOWN, "source": None},
        }
        
        result = engine.calculate(provenance)
        
        assert result.score <= 50
        assert len(result.caps_applied) > 0
    
    def test_estimate_penalty(self):
        """Test that estimates reduce confidence."""
        engine = ConfidenceEngine(estimate_penalty=15)
        
        provenance = {
            "income": {"state": ProvenanceState.VERIFIED, "source": "payroll_api"},
            "credit_score": {"state": ProvenanceState.ESTIMATED, "source": "model"},
        }
        
        result = engine.calculate(provenance)
        
        assert result.score == 85  # 100 - 15
    
    def test_contradiction_caps(self):
        """Test that contradictions cap confidence."""
        engine = ConfidenceEngine(contradiction_cap=60)
        
        provenance = {
            "income": {"state": ProvenanceState.VERIFIED, "source": "payroll_api"},
        }
        contradictions = ["Income stated as low but debt payments are high"]
        
        result = engine.calculate(provenance, contradictions=contradictions)
        
        assert result.score <= 60
        assert "Contradictions detected" in str(result.caps_applied)
    
    def test_verify_checklist_generation(self):
        """Test that verify checklist is generated correctly."""
        engine = ConfidenceEngine()
        
        provenance = {
            "income": {"state": ProvenanceState.PROVIDED, "source": "user"},
            "credit_score": {"state": ProvenanceState.UNKNOWN, "source": None},
        }
        
        result = engine.calculate(provenance)
        
        assert any("Verify income" in item for item in result.verify_checklist)
        assert any("credit_score" in item for item in result.verify_checklist)
    
    def test_missing_required_fields(self):
        """Test that missing required fields affect confidence."""
        engine = ConfidenceEngine(unknown_cap=50)
        
        provenance = {
            "income": {"state": ProvenanceState.VERIFIED, "source": "payroll_api"},
        }
        required = ["income", "credit_score", "dti_ratio"]
        
        result = engine.calculate(provenance, required_fields=required)
        
        assert result.score <= 50
        assert "credit_score" in str(result.verify_checklist)
        assert "dti_ratio" in str(result.verify_checklist)
