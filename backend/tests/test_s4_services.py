"""
S4 Backend Services Tests
Tests for version pinning, feature flags, delta reports, disablement, and LDA search
"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from app.services.version_pinning import ProgramVersionService, version_service
from app.services.feature_flags import FeatureFlagService, feature_flags, is_enabled
from app.services.delta_report import DeltaReportService, delta_service, ChangeImpact
from app.services.disablement import DownstreamDisablementService, disablement_service
from app.services.lda_search import LDASearchService, lda_search, SearchStatus


class TestVersionPinning:
    """Tests for ProgramVersionService."""
    
    def test_register_version(self):
        """Test registering a new program version."""
        service = ProgramVersionService()
        program_id = uuid4()
        
        version = service.register_version(
            program_id=program_id,
            version="1.0.0",
            rules=[{"id": "rule1", "condition": "score > 650"}],
            thresholds={"min_score": 650},
            created_by="test",
        )
        
        assert version.version == "1.0.0"
        assert version.program_id == program_id
        assert len(version.rules) == 1
        assert version.version_hash is not None
    
    def test_get_active_version(self):
        """Test getting active version for a program."""
        service = ProgramVersionService()
        program_id = uuid4()
        
        service.register_version(
            program_id=program_id,
            version="1.0.0",
            rules=[],
            thresholds={},
        )
        service.register_version(
            program_id=program_id,
            version="1.1.0",
            rules=[],
            thresholds={},
        )
        
        active = service.get_active_version(program_id)
        assert active is not None
        assert active.version == "1.1.0"
    
    def test_pin_decision(self):
        """Test pinning a decision to current version."""
        service = ProgramVersionService()
        program_id = uuid4()
        decision_id = uuid4()
        
        service.register_version(
            program_id=program_id,
            version="2.0.0",
            rules=[],
            thresholds={},
        )
        
        pin = service.pin_decision(decision_id, program_id)
        
        assert pin.version == "2.0.0"
        assert pin.decision_id == decision_id
    
    def test_get_pinned_version(self):
        """Test retrieving pinned version for decision."""
        service = ProgramVersionService()
        program_id = uuid4()
        decision_id = uuid4()
        
        service.register_version(
            program_id=program_id,
            version="1.5.0",
            rules=[{"id": "r1"}],
            thresholds={"min": 100},
        )
        
        service.pin_decision(decision_id, program_id)
        
        pinned = service.get_pinned_version(decision_id)
        assert pinned is not None
        assert pinned.version == "1.5.0"
        assert len(pinned.rules) == 1
    
    def test_deprecate_version(self):
        """Test deprecating a version."""
        service = ProgramVersionService()
        program_id = uuid4()
        
        service.register_version(
            program_id=program_id,
            version="1.0.0",
            rules=[],
            thresholds={},
        )
        
        result = service.deprecate_version(program_id, "1.0.0")
        assert result is True
        
        version = service.get_version(program_id, "1.0.0")
        assert version.deprecated_at is not None


class TestFeatureFlags:
    """Tests for FeatureFlagService."""
    
    def test_default_flags_initialized(self):
        """Test that default flags are initialized."""
        service = FeatureFlagService()
        
        flags = service.list_flags()
        assert len(flags) > 0
        assert any(f.key == "ENABLE_FAIRNESS_GATE" for f in flags)
    
    def test_is_enabled_default(self):
        """Test checking flag with default value."""
        service = FeatureFlagService()
        
        # LDA Search is enabled by default
        assert service.is_enabled("ENABLE_LDA_SEARCH") is True
        
        # Fairness gate is disabled by default
        assert service.is_enabled("ENABLE_FAIRNESS_GATE") is False
    
    def test_register_custom_flag(self):
        """Test registering a custom flag."""
        service = FeatureFlagService()
        
        flag = service.register_flag(
            key="CUSTOM_FLAG",
            name="Custom Flag",
            description="Test flag",
            default_value=True,
        )
        
        assert service.is_enabled("CUSTOM_FLAG") is True
    
    def test_update_flag(self):
        """Test updating a flag."""
        service = FeatureFlagService()
        
        service.register_flag(
            key="UPDATE_TEST",
            name="Update Test",
            description="Test",
            default_value=False,
        )
        
        assert service.is_enabled("UPDATE_TEST") is False
        
        service.update_flag("UPDATE_TEST", default_value=True)
        assert service.is_enabled("UPDATE_TEST") is True
    
    def test_list_flags_by_category(self):
        """Test listing flags by category."""
        service = FeatureFlagService()
        
        compliance_flags = service.list_flags(category="compliance")
        assert all(f.category == "compliance" for f in compliance_flags)
    
    def test_export_flags(self):
        """Test exporting flags for admin UI."""
        service = FeatureFlagService()
        
        exported = service.export_flags()
        assert len(exported) > 0
        assert "key" in exported[0]
        assert "current_value" in exported[0]


class TestDeltaReport:
    """Tests for DeltaReportService."""
    
    def test_generate_delta_report_no_changes(self):
        """Test generating report with no changes."""
        service = DeltaReportService()
        program_id = uuid4()
        
        old_version = {"rules": [], "thresholds": {}}
        new_version = {"rules": [], "thresholds": {}}
        
        report = service.generate_delta_report(
            program_id=program_id,
            from_version=old_version,
            to_version=new_version,
            from_version_str="1.0.0",
            to_version_str="1.0.1",
        )
        
        assert len(report.changes) == 0
        assert report.overall_impact == ChangeImpact.PATCH
    
    def test_generate_delta_report_rule_added(self):
        """Test detecting added rule."""
        service = DeltaReportService()
        program_id = uuid4()
        
        old_version = {"rules": [], "thresholds": {}}
        new_version = {"rules": [{"id": "new_rule", "condition": "x > 10"}], "thresholds": {}}
        
        report = service.generate_delta_report(
            program_id=program_id,
            from_version=old_version,
            to_version=new_version,
            from_version_str="1.0.0",
            to_version_str="2.0.0",
        )
        
        assert len(report.changes) == 1
        assert report.changes[0].change_type.value == "added"
    
    def test_generate_delta_report_breaking_change(self):
        """Test detecting breaking change."""
        service = DeltaReportService()
        program_id = uuid4()
        
        old_version = {"rules": [{"id": "rule1", "condition": "x > 10"}], "thresholds": {}}
        new_version = {"rules": [], "thresholds": {}}  # Rule removed
        
        report = service.generate_delta_report(
            program_id=program_id,
            from_version=old_version,
            to_version=new_version,
            from_version_str="1.0.0",
            to_version_str="2.0.0",
        )
        
        assert report.overall_impact == ChangeImpact.BREAKING
        assert report.breaking_changes_count == 1
    
    def test_export_report(self):
        """Test exporting report as JSON."""
        service = DeltaReportService()
        program_id = uuid4()
        
        report = service.generate_delta_report(
            program_id=program_id,
            from_version={"rules": [], "thresholds": {"min_score": 600}},
            to_version={"rules": [], "thresholds": {"min_score": 650}},
            from_version_str="1.0.0",
            to_version_str="1.1.0",
        )
        
        exported = service.export_report(report.report_id)
        assert exported is not None
        assert "from_version" in exported
        assert "changes" in exported


class TestDisablement:
    """Tests for DownstreamDisablementService."""
    
    def test_register_dependency(self):
        """Test registering program dependencies."""
        service = DownstreamDisablementService()
        parent = uuid4()
        child = uuid4()
        
        dep = service.register_dependency(parent, child)
        
        assert dep.parent_program_id == parent
        assert dep.child_program_id == child
    
    def test_get_dependency_chain(self):
        """Test getting full dependency chain."""
        service = DownstreamDisablementService()
        parent = uuid4()
        child1 = uuid4()
        child2 = uuid4()
        grandchild = uuid4()
        
        service.register_dependency(parent, child1)
        service.register_dependency(parent, child2)
        service.register_dependency(child1, grandchild)
        
        chain = service.get_dependency_chain(parent)
        
        assert len(chain) == 3
        assert child1 in chain
        assert child2 in chain
        assert grandchild in chain
    
    def test_verify_disablement_safe(self):
        """Test safety verification for disablement."""
        service = DownstreamDisablementService()
        parent = uuid4()
        child = uuid4()
        
        service.register_dependency(parent, child, is_critical=False)
        
        result = service.verify_disablement_safe(parent)
        assert result["can_disable"] is True
    
    def test_verify_disablement_blocked(self):
        """Test blocking disablement for critical dependencies."""
        service = DownstreamDisablementService()
        parent = uuid4()
        child = uuid4()
        
        service.register_dependency(parent, child, is_critical=True)
        
        result = service.verify_disablement_safe(parent)
        assert result["can_disable"] is False
        assert len(result["critical_blockers"]) == 1
    
    def test_disable_program(self):
        """Test disabling a program."""
        service = DownstreamDisablementService()
        program = uuid4()
        
        event = service.disable_program(
            program_id=program,
            reason="End of life",
            triggered_by="admin",
        )
        
        assert event is not None
        assert event.action.value == "disabled"
    
    def test_deprecate_program(self):
        """Test deprecating a program."""
        service = DownstreamDisablementService()
        program = uuid4()
        
        event = service.deprecate_program(
            program_id=program,
            reason="Superseded by v2",
            triggered_by="admin",
        )
        
        assert event is not None
        assert event.action.value == "deprecated"


class TestLDASearch:
    """Tests for LDASearchService."""
    
    def test_create_search(self):
        """Test creating an LDA search."""
        service = LDASearchService()
        program_id = uuid4()
        
        search = service.create_search(
            program_id=program_id,
            policy_rules=[{"id": "r1", "field": "score", "threshold": 650}],
            protected_attribute="race",
        )
        
        assert search.status == SearchStatus.PENDING
        assert search.program_id == program_id
    
    @pytest.mark.asyncio
    async def test_run_search(self):
        """Test running an LDA search."""
        service = LDASearchService()
        program_id = uuid4()
        
        search = service.create_search(
            program_id=program_id,
            policy_rules=[
                {"id": "r1", "field": "credit_score", "threshold": 650},
                {"id": "r2", "field": "dti", "threshold": 0.43},
            ],
            protected_attribute="ethnicity",
        )
        
        result = await service.run_search(search.search_id)
        
        assert result.status == SearchStatus.COMPLETED
        assert len(result.alternatives) > 0
    
    def test_export_search_results(self):
        """Test exporting search results."""
        service = LDASearchService()
        program_id = uuid4()
        
        search = service.create_search(
            program_id=program_id,
            policy_rules=[],
            protected_attribute="gender",
        )
        
        exported = service.export_search_results(search.search_id)
        assert exported is not None
        assert "search_id" in exported
        assert "status" in exported


class TestIntegration:
    """Integration tests for S4 services working together."""
    
    def test_version_pinning_with_delta_report(self):
        """Test version pinning integrates with delta reports."""
        version_svc = ProgramVersionService()
        delta_svc = DeltaReportService()
        program_id = uuid4()
        
        # Register v1
        v1 = version_svc.register_version(
            program_id=program_id,
            version="1.0.0",
            rules=[{"id": "r1", "condition": "x > 10"}],
            thresholds={"min": 10},
        )
        
        # Register v2
        v2 = version_svc.register_version(
            program_id=program_id,
            version="2.0.0",
            rules=[{"id": "r1", "condition": "x > 15"}],
            thresholds={"min": 15},
        )
        
        # Generate delta report
        report = delta_svc.generate_delta_report(
            program_id=program_id,
            from_version={"rules": v1.rules, "thresholds": v1.thresholds},
            to_version={"rules": v2.rules, "thresholds": v2.thresholds},
            from_version_str=v1.version,
            to_version_str=v2.version,
        )
        
        assert len(report.changes) > 0
    
    def test_feature_flag_guards_service(self):
        """Test feature flags can guard service behavior."""
        flag_svc = FeatureFlagService()
        
        flag_svc.register_flag(
            key="ENABLE_TEST_FEATURE",
            name="Test Feature",
            description="Test",
            default_value=False,
        )
        
        # Feature is off
        if flag_svc.is_enabled("ENABLE_TEST_FEATURE"):
            result = "feature_executed"
        else:
            result = "feature_skipped"
        
        assert result == "feature_skipped"
        
        # Enable feature
        flag_svc.update_flag("ENABLE_TEST_FEATURE", default_value=True)
        
        if flag_svc.is_enabled("ENABLE_TEST_FEATURE"):
            result = "feature_executed"
        else:
            result = "feature_skipped"
        
        assert result == "feature_executed"
