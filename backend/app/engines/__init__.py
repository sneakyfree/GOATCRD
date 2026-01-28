"""Engines package init."""
from app.engines.rules import RulesEngine, DEFAULT_PERSONAL_LOAN_RULESET
from app.engines.confidence import ConfidenceEngine, confidence_engine
from app.engines.explainability import ExplainabilityEngine, NoNewFactsViolation
from app.engines.scenario_builder import ScenarioBuilder, ProgramConfig, EXAMPLE_PROGRAM_CATALOG
from app.engines.ranking import RankingEngine, RankingMode
from app.engines.reason_codes import ReasonCodesEngine, reason_codes_engine, REASON_CODE_CATALOG
from app.engines.counterfactual import CounterfactualSimulator
from app.engines.audit_snapshot import AuditSnapshotEngine, audit_snapshot_engine
from app.engines.export import ExportEngine, export_engine
from app.engines.provenance import ProvenanceTracker, ProvenanceState, SourceType, create_provenance_tracker
from app.engines.credit_pulse import CreditPulseEngine, credit_pulse_engine, AlertType, AlertPriority
from app.engines.alternative_data import AlternativeDataEngine, alternative_data_engine, AltDataSource

__all__ = [
    # Core engines
    "RulesEngine",
    "DEFAULT_PERSONAL_LOAN_RULESET",
    "ConfidenceEngine",
    "confidence_engine",
    "ExplainabilityEngine",
    "NoNewFactsViolation",
    # Scenario engines
    "ScenarioBuilder",
    "ProgramConfig",
    "EXAMPLE_PROGRAM_CATALOG",
    "RankingEngine",
    "RankingMode",
    "ReasonCodesEngine",
    "reason_codes_engine",
    "REASON_CODE_CATALOG",
    # Simulation engines
    "CounterfactualSimulator",
    # Audit engines
    "AuditSnapshotEngine",
    "audit_snapshot_engine",
    # Export engines
    "ExportEngine",
    "export_engine",
    # Provenance engines
    "ProvenanceTracker",
    "ProvenanceState",
    "SourceType",
    "create_provenance_tracker",
    # Credit Pulse
    "CreditPulseEngine",
    "credit_pulse_engine",
    "AlertType",
    "AlertPriority",
    # Alternative Data
    "AlternativeDataEngine",
    "alternative_data_engine",
    "AltDataSource",
]
