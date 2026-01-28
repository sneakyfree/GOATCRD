"""
GOATCRD Scenario Service
Orchestrates scenario generation, ranking, and export
"""
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.engines import (
    ScenarioBuilder,
    RankingEngine,
    RankingMode,
    ReasonCodesEngine,
    CounterfactualSimulator,
    AuditSnapshotEngine,
    ExplainabilityEngine,
    EXAMPLE_PROGRAM_CATALOG,
)
from app.models import (
    Case,
    IntakeSnapshot,
    Scenario,
    ScenarioRun,
    Ranking,
    AuditSnapshot,
    EligibilityStatus,
)
from app.services.audit import AuditService


class ScenarioService:
    """
    Service for orchestrating scenario generation, ranking, and export.
    
    Integrates all engines to produce complete scenario results.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scenario_builder = ScenarioBuilder(EXAMPLE_PROGRAM_CATALOG)
        self.ranking_engine = RankingEngine()
        self.reason_codes_engine = ReasonCodesEngine()
        self.counterfactual_simulator = CounterfactualSimulator(EXAMPLE_PROGRAM_CATALOG)
        self.audit_snapshot_engine = AuditSnapshotEngine()
        self.audit_service = AuditService(db)
    
    async def run_scenarios(
        self,
        case_id: UUID,
        intake_snapshot_id: UUID,
        actor_id: UUID,
        actor_role: str,
    ) -> ScenarioRun:
        """
        Generate scenario universe for a case.
        
        Returns ScenarioRun with all generated scenarios.
        """
        # Get intake snapshot
        result = await self.db.execute(
            select(IntakeSnapshot).where(IntakeSnapshot.id == intake_snapshot_id)
        )
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            raise ValueError("Intake snapshot not found")
        
        # Extract data and provenance
        intake_data = snapshot.normalized_data
        provenance = snapshot.provenance
        
        # Get consumer state for geography filtering
        consumer_state = intake_data.get("state")
        
        # Build scenarios
        build_result = self.scenario_builder.build(
            intake_data=intake_data,
            provenance=provenance,
            intake_snapshot_id=intake_snapshot_id,
            consumer_state=consumer_state,
        )
        
        # Create scenario run record
        run = ScenarioRun(
            case_id=case_id,
            intake_snapshot_id=intake_snapshot_id,
            program_versions=build_result.program_versions,
            ruleset_versions={},
            started_at=build_result.started_at,
            completed_at=build_result.completed_at,
            total_scenarios=build_result.total_scenarios,
            eligible_count=len(build_result.eligible),
            refer_count=len(build_result.refer),
            not_eligible_count=len(build_result.not_eligible),
        )
        self.db.add(run)
        await self.db.flush()
        
        # Create scenario records
        all_scenarios = build_result.eligible + build_result.refer + build_result.not_eligible
        for scenario_result in all_scenarios:
            scenario = Scenario(
                scenario_run_id=run.id,
                program_id=scenario_result.program_id,
                dedup_key=scenario_result.dedup_key,
                status=scenario_result.status,
                rule_hits=scenario_result.rule_hits,
                missing_inputs=scenario_result.missing_inputs,
                reason_codes=scenario_result.reason_codes,
                pricing=scenario_result.pricing,
                pricing_source=scenario_result.pricing_source,
                confidence_score=scenario_result.confidence_score,
                confidence_drivers=scenario_result.confidence_drivers,
                confidence_caps=scenario_result.confidence_caps,
                verify_checklist=scenario_result.verify_checklist,
            )
            self.db.add(scenario)
        
        # Log audit event
        await self.audit_service.log_scenario_run(
            case_id=case_id,
            run_id=run.id,
            actor_id=actor_id,
            actor_role=actor_role,
        )
        
        await self.db.flush()
        await self.db.refresh(run)
        
        return run
    
    async def get_rankings(
        self,
        scenario_run_id: UUID,
        mode: str,
    ) -> dict[str, Any]:
        """
        Get ranked scenarios for a run in specified mode.
        """
        # Get scenarios for run
        result = await self.db.execute(
            select(Scenario).where(Scenario.scenario_run_id == scenario_run_id)
        )
        scenarios = list(result.scalars().all())
        
        # Convert to ScenarioResult format for ranking engine
        from app.engines.scenario_builder import ScenarioResult
        
        scenario_results = [
            ScenarioResult(
                scenario_id=s.id,
                dedup_key=s.dedup_key,
                program_id=s.program_id,
                program_name="Program",  # Would need to join with programs
                status=s.status,
                rule_hits=s.rule_hits,
                missing_inputs=s.missing_inputs,
                reason_codes=s.reason_codes,
                confidence_score=s.confidence_score,
                confidence_drivers=s.confidence_drivers,
                confidence_caps=s.confidence_caps,
                verify_checklist=s.verify_checklist,
                pricing=s.pricing,
                pricing_source=s.pricing_source or "unknown",
            )
            for s in scenarios
        ]
        
        # Rank scenarios
        ranking_mode = RankingMode(mode)
        ranking_result = self.ranking_engine.rank(scenario_results, ranking_mode)
        
        # Store ranking
        ranking = Ranking(
            scenario_run_id=scenario_run_id,
            mode=ranking_mode,
            ranked_scenarios=[
                {
                    "scenario_id": str(rs.scenario.scenario_id),
                    "rank": rs.rank,
                    "score": rs.score,
                    "gated": rs.gated,
                    "gating_reason": rs.gating_reason,
                }
                for rs in ranking_result.ranked_scenarios
            ],
            gated_scenarios=[
                {
                    "scenario_id": str(rs.scenario.scenario_id),
                    "gating_reason": rs.gating_reason,
                }
                for rs in ranking_result.gated_scenarios
            ],
        )
        self.db.add(ranking)
        await self.db.flush()
        
        return {
            "mode": mode,
            "ranked_scenarios": ranking.ranked_scenarios,
            "gated_scenarios": ranking.gated_scenarios,
            "sensitivity_notes": ranking_result.sensitivity_notes,
        }
    
    async def simulate_counterfactual(
        self,
        case_id: UUID,
        hypothetical_changes: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Run What-If simulation for a case.
        """
        # Get latest intake snapshot for case
        result = await self.db.execute(
            select(IntakeSnapshot)
            .where(IntakeSnapshot.case_id == case_id)
            .order_by(IntakeSnapshot.created_at.desc())
            .limit(1)
        )
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            raise ValueError("No intake snapshot found for case")
        
        # Run simulation
        simulation_result = self.counterfactual_simulator.simulate(
            case_id=case_id,
            original_data=snapshot.normalized_data,
            original_provenance=snapshot.provenance,
            hypothetical_changes=hypothetical_changes,
            intake_snapshot_id=snapshot.id,
        )
        
        return {
            "case_id": str(simulation_result.case_id),
            "hypothetical_changes": simulation_result.hypothetical_changes,
            "validated_changes": simulation_result.validated_changes,
            "rejected_changes": simulation_result.rejected_changes,
            "status_changes": [
                {
                    "program_id": str(sc.program_id),
                    "program_name": sc.program_name,
                    "original_status": sc.original_status.value,
                    "simulated_status": sc.simulated_status.value,
                    "changed": sc.changed,
                    "resolved_reason_codes": sc.resolved_reason_codes,
                }
                for sc in simulation_result.status_changes
            ],
            "changes_summary": simulation_result.changes_summary,
            "confidence": simulation_result.confidence,
            "confidence_reason": simulation_result.confidence_reason,
            "disclaimer": simulation_result.disclaimer,
        }
    
    async def generate_explanations(
        self,
        scenario_id: UUID,
        layers: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Generate explanations for a scenario.
        """
        layers = layers or ["consumer", "pro"]
        
        # Get scenario
        result = await self.db.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        scenario = result.scalar_one_or_none()
        
        if not scenario:
            raise ValueError("Scenario not found")
        
        # Get intake data for context
        run_result = await self.db.execute(
            select(ScenarioRun).where(ScenarioRun.id == scenario.scenario_run_id)
        )
        run = run_result.scalar_one_or_none()
        
        snapshot_result = await self.db.execute(
            select(IntakeSnapshot).where(IntakeSnapshot.id == run.intake_snapshot_id)
        )
        snapshot = snapshot_result.scalar_one_or_none()
        
        # Build explanation context
        context = {
            "program_name": "Credit Program",
            "positive_factors": "Based on your profile",
            "missing_items": "\n".join(f"- {item}" for item in scenario.missing_inputs),
            "reason_summary": "\n".join(f"- {code}" for code in scenario.reason_codes),
            "improvement_suggestions": "See improvement path below",
            "estimated_payment": scenario.pricing.get("monthly_payment", "N/A") if scenario.pricing else "N/A",
            "next_steps": "Review your options and contact a professional if needed",
            "why_matters": "These items help verify your eligibility",
            "confidence_score": scenario.confidence_score,
            "pricing_source": scenario.pricing_source or "unknown",
        }
        
        # Generate explanations
        engine = ExplainabilityEngine({**snapshot.normalized_data, **context})
        
        explanations = {}
        for layer in layers:
            try:
                explanation = engine.generate(
                    status=scenario.status.value,
                    layer=layer,
                    context=context,
                )
                explanations[layer] = {
                    "content": explanation.content,
                    "field_references": explanation.field_references,
                }
            except Exception as e:
                explanations[layer] = {
                    "content": f"Explanation generation error: {e}",
                    "field_references": [],
                }
        
        # Generate improvement path if NOT_ELIGIBLE
        improvement_path = []
        if scenario.status == EligibilityStatus.NOT_ELIGIBLE:
            improvement_path = self.reason_codes_engine.get_improvement_path(
                scenario.reason_codes
            )
        
        return {
            "scenario_id": str(scenario_id),
            "status": scenario.status.value,
            "explanations": explanations,
            "improvement_path": improvement_path,
        }
    
    async def create_audit_snapshot(
        self,
        case_id: UUID,
        scenario_run_id: UUID,
        actor_id: UUID | None = None,
    ) -> AuditSnapshot:
        """
        Create immutable audit snapshot for a scenario run.
        """
        # Get run
        run_result = await self.db.execute(
            select(ScenarioRun).where(ScenarioRun.id == scenario_run_id)
        )
        run = run_result.scalar_one_or_none()
        
        if not run:
            raise ValueError("Scenario run not found")
        
        # Get intake snapshot
        snapshot_result = await self.db.execute(
            select(IntakeSnapshot).where(IntakeSnapshot.id == run.intake_snapshot_id)
        )
        intake_snapshot = snapshot_result.scalar_one_or_none()
        
        # Get scenarios summary
        scenarios_result = await self.db.execute(
            select(Scenario).where(Scenario.scenario_run_id == scenario_run_id)
        )
        scenarios = list(scenarios_result.scalars().all())
        
        reason_codes = []
        for s in scenarios:
            reason_codes.extend(s.reason_codes)
        
        scenarios_summary = {
            "total": len(scenarios),
            "eligible_count": run.eligible_count,
            "refer_count": run.refer_count,
            "not_eligible_count": run.not_eligible_count,
        }
        
        # Create snapshot data
        snapshot_data = self.audit_snapshot_engine.create_snapshot(
            case_id=case_id,
            intake_snapshot_id=run.intake_snapshot_id,
            intake_data=intake_snapshot.normalized_data,
            provenance=intake_snapshot.provenance,
            consent_states={},  # Would populate from consents
            program_versions=run.program_versions,
            ruleset_versions=run.ruleset_versions,
            scenarios_summary=scenarios_summary,
            rankings_summary={},
            reason_codes_issued=list(set(reason_codes)),
            created_by=actor_id,
        )
        
        # Store in database
        audit_snapshot = AuditSnapshot(
            case_id=case_id,
            intake_snapshot_id=run.intake_snapshot_id,
            consent_states={},
            program_versions=run.program_versions,
            ruleset_versions=run.ruleset_versions,
            scenario_run_id=scenario_run_id,
            scenarios_summary=scenarios_summary,
            rankings_summary={},
            reason_codes_summary=list(set(reason_codes)),
            app_version=snapshot_data.version_pins.app_version,
            feature_flags=snapshot_data.version_pins.feature_flags,
            snapshot_hash=snapshot_data.snapshot_hash,
        )
        self.db.add(audit_snapshot)
        await self.db.flush()
        await self.db.refresh(audit_snapshot)
        
        return audit_snapshot
