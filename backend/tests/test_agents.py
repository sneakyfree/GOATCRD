"""
Tests for GOATCRD Agentic Crew
"""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.agents.crew import (
    AgentOrchestrator,
    IntakeSpecialist,
    ScenarioAnalyst,
    ComplianceReviewer,
    AgentContext,
    AgentTask,
    AgentRole,
)


class TestIntakeSpecialist:
    """Test suite for IntakeSpecialist agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = IntakeSpecialist()
        self.context = AgentContext(
            case_id=uuid4(),
            consumer_id=uuid4(),
            intake_data={
                "annual_income": 75000,
                "credit_score": 720,
                "dti_ratio": 0.35,
            },
            provenance={},
            scenarios=[],
        )
    
    @pytest.mark.asyncio
    async def test_validate_intake_identifies_missing_fields(self):
        """Test that missing fields are identified."""
        decision = await self.agent.execute(
            action="validate_intake",
            context=self.context,
            parameters={},
        )
        
        assert decision is not None
    
    @pytest.mark.asyncio
    async def test_suggest_missing_fields(self):
        """Test field suggestion capability."""
        decision = await self.agent.execute(
            action="suggest_missing",
            context=self.context,
            parameters={},
        )
        
        assert decision is not None
        assert decision.reasoning is not None
    
    @pytest.mark.asyncio
    async def test_detect_inconsistencies(self):
        """Test inconsistency detection."""
        context = AgentContext(
            case_id=uuid4(),
            consumer_id=uuid4(),
            intake_data={
                "annual_income": 30000,
                "monthly_rent": 4000,
                "credit_score": 800,
            },
            provenance={},
            scenarios=[],
        )
        
        decision = await self.agent.execute(
            action="detect_inconsistencies",
            context=context,
            parameters={},
        )
        
        assert decision is not None
    
    def test_capabilities_includes_expected_actions(self):
        """Test that capabilities are properly defined."""
        caps = self.agent.capabilities
        
        assert "validate_intake" in caps
        assert "suggest_missing_fields" in caps
        assert "detect_inconsistencies" in caps


class TestScenarioAnalyst:
    """Test suite for ScenarioAnalyst agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = ScenarioAnalyst()
        self.context = AgentContext(
            case_id=uuid4(),
            consumer_id=uuid4(),
            intake_data={
                "annual_income": 85000,
                "credit_score": 740,
            },
            provenance={},
            scenarios=[
                {"id": "1", "program_name": "Prime Loan", "status": "eligible", "confidence_score": 90},
                {"id": "2", "program_name": "Standard Loan", "status": "eligible", "confidence_score": 85},
                {"id": "3", "program_name": "Express Loan", "status": "refer", "confidence_score": 60},
            ],
        )
    
    @pytest.mark.asyncio
    async def test_analyze_scenarios(self):
        """Test scenario analysis."""
        decision = await self.agent.execute(
            action="analyze_scenarios",
            context=self.context,
            parameters={},
        )
        
        assert decision is not None
        assert decision.decision_type == "analysis"
    
    @pytest.mark.asyncio
    async def test_recommend_ranking(self):
        """Test ranking recommendation."""
        decision = await self.agent.execute(
            action="recommend_ranking",
            context=self.context,
            parameters={"mode": "consumer_first"},
        )
        
        assert decision is not None
    
    @pytest.mark.asyncio
    async def test_identify_improvements(self):
        """Test improvement identification."""
        decision = await self.agent.execute(
            action="identify_improvements",
            context=self.context,
            parameters={},
        )
        
        assert decision is not None
    
    def test_capabilities_includes_expected_actions(self):
        """Test that capabilities are properly defined."""
        caps = self.agent.capabilities
        
        assert "analyze_scenarios" in caps
        assert "recommend_ranking" in caps
        assert "identify_improvements" in caps


class TestComplianceReviewer:
    """Test suite for ComplianceReviewer agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.agent = ComplianceReviewer()
        self.context = AgentContext(
            case_id=uuid4(),
            consumer_id=uuid4(),
            intake_data={
                "annual_income": 50000,
                "credit_score": 640,
            },
            provenance={},
            scenarios=[
                {"id": "1", "program_name": "Prime Loan", "status": "not_eligible", 
                 "reason_codes": ["RC001", "RC002"]},
            ],
        )
    
    @pytest.mark.asyncio
    async def test_review_adverse_action(self):
        """Test adverse action review."""
        decision = await self.agent.execute(
            action="review_adverse_action",
            context=self.context,
            parameters={"scenario_id": "1"},
        )
        
        assert decision is not None
        assert decision.requires_human_review is True
    
    @pytest.mark.asyncio
    async def test_check_fair_lending(self):
        """Test fair lending check."""
        decision = await self.agent.execute(
            action="check_fair_lending",
            context=self.context,
            parameters={},
        )
        
        assert decision is not None
    
    def test_capabilities_includes_expected_actions(self):
        """Test that capabilities are properly defined."""
        caps = self.agent.capabilities
        
        assert "review_adverse_action" in caps
        assert "check_fair_lending" in caps


class TestAgentOrchestrator:
    """Test suite for AgentOrchestrator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = AgentOrchestrator()
        self.context = AgentContext(
            case_id=uuid4(),
            consumer_id=uuid4(),
            intake_data={"credit_score": 720, "annual_income": 80000},
            provenance={},
            scenarios=[],
        )
    
    @pytest.mark.asyncio
    async def test_run_intake_review_workflow(self):
        """Test intake review workflow execution."""
        decisions = await self.orchestrator.run_workflow("intake_review", self.context)
        
        assert len(decisions) > 0
        intake_decisions = [d for d in decisions if d.agent_role == AgentRole.INTAKE_SPECIALIST]
        assert len(intake_decisions) > 0
    
    @pytest.mark.asyncio
    async def test_run_scenario_analysis_workflow(self):
        """Test scenario analysis workflow."""
        self.context.scenarios = [
            {"id": "1", "status": "eligible", "program_name": "Test"},
        ]
        
        decisions = await self.orchestrator.run_workflow("scenario_analysis", self.context)
        
        assert len(decisions) > 0
    
    @pytest.mark.asyncio
    async def test_run_full_evaluation_workflow(self):
        """Test full evaluation workflow."""
        self.context.scenarios = [
            {"id": "1", "status": "eligible", "program_name": "Test", "reason_codes": []},
        ]
        
        decisions = await self.orchestrator.run_workflow("full_evaluation", self.context)
        
        roles_involved = set(d.agent_role for d in decisions)
        assert AgentRole.INTAKE_SPECIALIST in roles_involved


class TestAgentContext:
    """Test AgentContext dataclass."""
    
    def test_context_creation(self):
        """Test that context can be created."""
        context = AgentContext(
            case_id=uuid4(),
            consumer_id=uuid4(),
            intake_data={"test": "data"},
            provenance={},
        )
        
        assert context.case_id is not None
        assert context.intake_data == {"test": "data"}
    
    def test_context_with_scenarios(self):
        """Test context with scenarios."""
        context = AgentContext(
            case_id=uuid4(),
            consumer_id=uuid4(),
            intake_data={},
            provenance={},
            scenarios=[{"id": "1"}],
        )
        
        assert len(context.scenarios) == 1


class TestAgentTask:
    """Test AgentTask dataclass."""
    
    def test_task_creation(self):
        """Test that task can be created."""
        task = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.INTAKE_SPECIALIST,
            action="validate_intake",
            parameters={},
        )
        
        assert task.task_id is not None
        assert task.agent_role == AgentRole.INTAKE_SPECIALIST
        assert task.action == "validate_intake"
    
    def test_task_with_priority(self):
        """Test task with priority."""
        from app.agents.crew import TaskPriority
        
        task = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.COMPLIANCE_REVIEWER,
            action="review_adverse_action",
            parameters={},
            priority=TaskPriority.HIGH,
        )
        
        assert task.priority == TaskPriority.HIGH


class TestAgentRole:
    """Test AgentRole enum."""
    
    def test_intake_specialist_role(self):
        """Test intake specialist role value."""
        assert AgentRole.INTAKE_SPECIALIST.value == "intake_specialist"
    
    def test_scenario_analyst_role(self):
        """Test scenario analyst role value."""
        assert AgentRole.SCENARIO_ANALYST.value == "scenario_analyst"
    
    def test_compliance_reviewer_role(self):
        """Test compliance reviewer role value."""
        assert AgentRole.COMPLIANCE_REVIEWER.value == "compliance_reviewer"
