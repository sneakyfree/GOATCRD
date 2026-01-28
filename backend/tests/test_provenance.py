"""
GOATCRD Tests - Provenance Tracker
"""
import pytest
from uuid import uuid4

from app.engines.provenance import (
    ProvenanceTracker,
    ProvenanceState,
    SourceType,
    create_provenance_tracker,
)


class TestProvenanceTracker:
    """Tests for the provenance tracker."""
    
    def test_set_provenance(self):
        """Test setting provenance for a field."""
        tracker = create_provenance_tracker()
        
        record = tracker.set_provenance(
            field_name="annual_income",
            value=75000,
            state=ProvenanceState.PROVIDED,
            source_type=SourceType.CONSUMER_INPUT,
        )
        
        assert record.field_name == "annual_income"
        assert record.state == ProvenanceState.PROVIDED
        assert record.source_type == SourceType.CONSUMER_INPUT
    
    def test_upgrade_provenance(self):
        """Test upgrading provenance state."""
        tracker = create_provenance_tracker()
        
        # Set as provided
        tracker.set_provenance(
            field_name="annual_income",
            value=75000,
            state=ProvenanceState.PROVIDED,
            source_type=SourceType.CONSUMER_INPUT,
        )
        
        # Upgrade to verified
        record = tracker.upgrade_provenance(
            field_name="annual_income",
            new_state=ProvenanceState.VERIFIED,
            source_type=SourceType.PAYROLL_API,
            verification_method="payroll_pull",
        )
        
        assert record is not None
        assert record.state == ProvenanceState.VERIFIED
        assert record.source_type == SourceType.PAYROLL_API
    
    def test_cannot_downgrade_provenance(self):
        """Test that provenance cannot be downgraded."""
        tracker = create_provenance_tracker()
        
        # Set as verified
        tracker.set_provenance(
            field_name="credit_score",
            value=720,
            state=ProvenanceState.VERIFIED,
            source_type=SourceType.CREDIT_BUREAU,
        )
        
        # Try to downgrade to provided
        record = tracker.upgrade_provenance(
            field_name="credit_score",
            new_state=ProvenanceState.PROVIDED,
            source_type=SourceType.CONSUMER_INPUT,
        )
        
        # Should remain verified
        assert record.state == ProvenanceState.VERIFIED
    
    def test_contradiction_detection(self):
        """Test that contradictions are detected on value change."""
        tracker = create_provenance_tracker()
        
        # Set initial value
        tracker.set_provenance(
            field_name="annual_income",
            value=75000,
            state=ProvenanceState.PROVIDED,
            source_type=SourceType.CONSUMER_INPUT,
        )
        
        # Set different value from different source
        tracker.set_provenance(
            field_name="annual_income",
            value=80000,
            state=ProvenanceState.VERIFIED,
            source_type=SourceType.PAYROLL_API,
        )
        
        # Should have a contradiction
        contradictions = tracker.get_contradictions()
        assert len(contradictions) == 1
        assert contradictions[0].field_name == "annual_income"
    
    def test_confidence_calculation(self):
        """Test confidence impact calculation."""
        tracker = create_provenance_tracker()
        
        # Mix of provenance states
        tracker.set_provenance("income", 75000, ProvenanceState.VERIFIED, SourceType.PAYROLL_API)
        tracker.set_provenance("rent", 1500, ProvenanceState.PROVIDED, SourceType.CONSUMER_INPUT)
        tracker.set_provenance("savings", 10000, ProvenanceState.ESTIMATED, SourceType.ESTIMATED)
        
        impact = tracker.calculate_confidence_impact()
        
        assert impact["score"] >= 0
        assert impact["score"] <= 100
        assert "breakdown" in impact
        assert impact["breakdown"]["verified"] == 1
        assert impact["breakdown"]["provided"] == 1
        assert impact["breakdown"]["estimated"] == 1
    
    def test_verify_checklist_generation(self):
        """Test verification checklist generation."""
        tracker = create_provenance_tracker()
        
        tracker.set_provenance("income", 75000, ProvenanceState.PROVIDED, SourceType.CONSUMER_INPUT)
        tracker.set_provenance("score", 720, ProvenanceState.VERIFIED, SourceType.CREDIT_BUREAU)
        
        checklist = tracker.generate_verify_checklist()
        
        # Only provided fields should be in checklist
        assert len(checklist) == 1
        assert checklist[0]["field"] == "income"
        assert checklist[0]["priority"] == "recommended"
