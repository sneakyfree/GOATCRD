"""
GOATCRD Agentic Crew Framework
Multi-agent orchestration for intelligent credit decisioning
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
from uuid import UUID, uuid4


class AgentRole(str, Enum):
    """Roles for GOATCRD specialist agents."""
    
    INTAKE_SPECIALIST = "intake_specialist"
    VERIFICATION_SPECIALIST = "verification_specialist"
    SCENARIO_ANALYST = "scenario_analyst"
    COMPLIANCE_REVIEWER = "compliance_reviewer"
    CONSUMER_ADVOCATE = "consumer_advocate"
    COACH = "coach"
    ORCHESTRATOR = "orchestrator"


class AgentStatus(str, Enum):
    """Agent execution status."""
    
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskPriority(str, Enum):
    """Task priority levels."""
    
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class AgentContext:
    """Context passed to agents."""
    
    case_id: UUID
    consumer_id: UUID
    intake_data: dict[str, Any]
    provenance: dict[str, Any]
    scenarios: list[dict] | None = None
    rankings: dict[str, Any] | None = None
    alerts: list[dict] = field(default_factory=list)
    
    # Workflow state
    workflow_id: UUID | None = None
    step_number: int = 0
    
    # Shared memory for inter-agent communication
    shared_memory: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentTask:
    """Task for an agent to execute."""
    
    task_id: UUID
    agent_role: AgentRole
    action: str
    parameters: dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    depends_on: list[UUID] = field(default_factory=list)
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    completed_at: datetime | None = None
    
    status: AgentStatus = AgentStatus.IDLE
    result: Any = None
    error: str | None = None


@dataclass
class AgentDecision:
    """Decision made by an agent."""
    
    decision_id: UUID
    agent_role: AgentRole
    decision_type: str
    
    recommendation: str
    confidence: int  # 0-100
    reasoning: str
    
    requires_human_review: bool = False
    review_reason: str | None = None
    
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class BaseAgent(ABC):
    """
    Base class for GOATCRD specialist agents.
    
    Each agent has a specific role and set of capabilities.
    Agents must never hallucinate approvals or pricing.
    """
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.status = AgentStatus.IDLE
        self.confidence_threshold = 70  # Require human review below this
    
    @property
    @abstractmethod
    def capabilities(self) -> list[str]:
        """List of actions this agent can perform."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        action: str,
        context: AgentContext,
        parameters: dict[str, Any],
    ) -> AgentDecision:
        """Execute an action and return a decision."""
        pass
    
    def _create_decision(
        self,
        decision_type: str,
        recommendation: str,
        confidence: int,
        reasoning: str,
    ) -> AgentDecision:
        """Create a decision with automatic human review flagging."""
        requires_review = confidence < self.confidence_threshold
        
        return AgentDecision(
            decision_id=uuid4(),
            agent_role=self.role,
            decision_type=decision_type,
            recommendation=recommendation,
            confidence=confidence,
            reasoning=reasoning,
            requires_human_review=requires_review,
            review_reason="Confidence below threshold" if requires_review else None,
        )


class IntakeSpecialist(BaseAgent):
    """
    Agent specialized in intake collection and validation.
    """
    
    def __init__(self):
        super().__init__(AgentRole.INTAKE_SPECIALIST)
    
    @property
    def capabilities(self) -> list[str]:
        return [
            "validate_intake",
            "suggest_missing_fields",
            "detect_inconsistencies",
            "recommend_verification",
        ]
    
    async def execute(
        self,
        action: str,
        context: AgentContext,
        parameters: dict[str, Any],
    ) -> AgentDecision:
        if action == "validate_intake":
            return await self._validate_intake(context)
        elif action == "suggest_missing_fields":
            return await self._suggest_missing(context)
        elif action == "detect_inconsistencies":
            return await self._detect_inconsistencies(context)
        else:
            return self._create_decision(
                "error",
                f"Unknown action: {action}",
                0,
                "Action not supported by this agent",
            )
    
    async def _validate_intake(self, context: AgentContext) -> AgentDecision:
        """Validate intake data completeness and quality."""
        required_fields = [
            "annual_income", "credit_score", "employment_status",
            "loan_amount", "loan_purpose",
        ]
        
        missing = [f for f in required_fields if f not in context.intake_data]
        
        if not missing:
            return self._create_decision(
                "validation",
                "Intake data is complete",
                95,
                "All required fields are present",
            )
        else:
            return self._create_decision(
                "validation",
                f"Missing required fields: {', '.join(missing)}",
                60,
                f"{len(missing)} required fields are missing",
            )
    
    async def _suggest_missing(self, context: AgentContext) -> AgentDecision:
        """Suggest fields that would improve scenario results."""
        suggestions = []
        
        # Check for fields that could unlock more programs
        if "employer_name" not in context.intake_data:
            suggestions.append("employer_name (enables employment verification)")
        
        if "bank_balance" not in context.intake_data:
            suggestions.append("bank_balance (improves cash flow analysis)")
        
        if suggestions:
            return self._create_decision(
                "suggestions",
                f"Consider adding: {', '.join(suggestions)}",
                80,
                "These fields may unlock additional program options",
            )
        else:
            return self._create_decision(
                "suggestions",
                "No additional fields recommended",
                90,
                "Intake data is comprehensive",
            )
    
    async def _detect_inconsistencies(self, context: AgentContext) -> AgentDecision:
        """Detect potential inconsistencies in intake data."""
        issues = []
        data = context.intake_data
        
        # Income vs stated employer
        if data.get("employment_status") == "unemployed" and data.get("annual_income", 0) > 50000:
            issues.append("High income reported with unemployed status")
        
        # DTI check
        income = data.get("annual_income", 0)
        debt = data.get("monthly_debt_payments", 0) * 12
        if income > 0 and debt / income > 0.6:
            issues.append("Debt-to-income ratio appears very high")
        
        if issues:
            return self._create_decision(
                "inconsistencies",
                f"Found {len(issues)} potential issue(s)",
                60,
                "; ".join(issues),
            )
        else:
            return self._create_decision(
                "inconsistencies",
                "No inconsistencies detected",
                90,
                "Data appears internally consistent",
            )


class ScenarioAnalyst(BaseAgent):
    """
    Agent specialized in scenario analysis and recommendations.
    """
    
    def __init__(self):
        super().__init__(AgentRole.SCENARIO_ANALYST)
    
    @property
    def capabilities(self) -> list[str]:
        return [
            "analyze_scenarios",
            "recommend_ranking",
            "identify_improvements",
            "simulate_counterfactual",
        ]
    
    async def execute(
        self,
        action: str,
        context: AgentContext,
        parameters: dict[str, Any],
    ) -> AgentDecision:
        if action == "analyze_scenarios":
            return await self._analyze_scenarios(context)
        elif action == "recommend_ranking":
            return await self._recommend_ranking(context, parameters)
        elif action == "identify_improvements":
            return await self._identify_improvements(context)
        else:
            return self._create_decision(
                "error",
                f"Unknown action: {action}",
                0,
                "Action not supported",
            )
    
    async def _analyze_scenarios(self, context: AgentContext) -> AgentDecision:
        """Analyze scenario results."""
        scenarios = context.scenarios or []
        
        eligible = [s for s in scenarios if s.get("status") == "eligible"]
        refer = [s for s in scenarios if s.get("status") == "refer"]
        
        if eligible:
            return self._create_decision(
                "analysis",
                f"Found {len(eligible)} eligible program(s)",
                85,
                f"Consumer qualifies for {len(eligible)} programs. {len(refer)} need more information.",
            )
        elif refer:
            return self._create_decision(
                "analysis",
                f"{len(refer)} program(s) need additional information",
                70,
                "No immediate eligibility, but some programs may work with verification",
            )
        else:
            return self._create_decision(
                "analysis",
                "No eligible programs found",
                90,
                "Consumer does not meet current program requirements",
            )
    
    async def _recommend_ranking(
        self,
        context: AgentContext,
        parameters: dict[str, Any],
    ) -> AgentDecision:
        """Recommend best ranking mode for consumer."""
        goals = parameters.get("consumer_goals", {})
        
        if goals.get("priority_low_payment"):
            mode = "lowest_payment"
            reasoning = "Consumer prioritizes low monthly payment"
        elif goals.get("priority_fast_close"):
            mode = "fastest_close"
            reasoning = "Consumer needs fast approval"
        elif goals.get("priority_certainty"):
            mode = "highest_certainty"
            reasoning = "Consumer wants most reliable option"
        else:
            mode = "lowest_total_cost"
            reasoning = "Default to lowest total cost for best value"
        
        return self._create_decision(
            "ranking_recommendation",
            f"Recommend '{mode}' ranking",
            80,
            reasoning,
        )
    
    async def _identify_improvements(self, context: AgentContext) -> AgentDecision:
        """Identify actionable improvements for eligibility."""
        scenarios = context.scenarios or []
        
        # Collect reason codes from non-eligible scenarios
        reason_codes = set()
        for s in scenarios:
            if s.get("status") != "eligible":
                reason_codes.update(s.get("reason_codes", []))
        
        if not reason_codes:
            return self._create_decision(
                "improvements",
                "No specific improvements identified",
                70,
                "Already eligible or no actionable reason codes",
            )
        
        # Map to actionable improvements (simplified)
        improvements = []
        if "RC002" in reason_codes:  # Credit score
            improvements.append("Improve credit score")
        if "RC003" in reason_codes:  # DTI
            improvements.append("Reduce debt-to-income ratio")
        if "RC004" in reason_codes:  # Income
            improvements.append("Document additional income sources")
        
        return self._create_decision(
            "improvements",
            f"Top improvements: {', '.join(improvements[:3])}",
            75,
            f"Based on {len(reason_codes)} reason code(s) from scenarios",
        )


class ComplianceReviewer(BaseAgent):
    """
    Agent specialized in compliance review.
    """
    
    def __init__(self):
        super().__init__(AgentRole.COMPLIANCE_REVIEWER)
        self.confidence_threshold = 90  # Higher threshold for compliance
    
    @property
    def capabilities(self) -> list[str]:
        return [
            "review_adverse_action",
            "verify_disclosures",
            "check_fair_lending",
        ]
    
    async def execute(
        self,
        action: str,
        context: AgentContext,
        parameters: dict[str, Any],
    ) -> AgentDecision:
        if action == "review_adverse_action":
            return await self._review_adverse_action(context)
        elif action == "check_fair_lending":
            return await self._check_fair_lending(context)
        else:
            return self._create_decision(
                "error",
                f"Unknown action: {action}",
                0,
                "Action not supported",
            )
    
    async def _review_adverse_action(self, context: AgentContext) -> AgentDecision:
        """Review adverse action notices for compliance."""
        scenarios = context.scenarios or []
        
        not_eligible = [s for s in scenarios if s.get("status") == "not_eligible"]
        
        for scenario in not_eligible:
            reason_codes = scenario.get("reason_codes", [])
            if not reason_codes:
                return self._create_decision(
                    "compliance_review",
                    "REQUIRES REVIEW: Missing reason codes for denial",
                    20,
                    "Adverse action requires specific reason codes per ECOA",
                )
        
        if not_eligible:
            return self._create_decision(
                "compliance_review",
                "Adverse action notices appear compliant",
                85,
                f"All {len(not_eligible)} denials have proper reason codes",
            )
        else:
            return self._create_decision(
                "compliance_review",
                "No adverse action review needed",
                95,
                "No denials to review",
            )
    
    async def _check_fair_lending(self, context: AgentContext) -> AgentDecision:
        """Check for fair lending compliance."""
        # This would integrate with fairness testing in production
        return self._create_decision(
            "fair_lending",
            "Fair lending check requires production fairness engine",
            50,
            "This check requires the full fairness testing pipeline",
        )


class CoachAgent(BaseAgent):
    """
    Agent specialized in proactive consumer guidance.
    
    GUARDRAILS:
    - Never promise specific outcomes or approval
    - All suggestions are directional, not guarantees
    - Respects consent boundaries
    """
    
    def __init__(self):
        super().__init__(AgentRole.COACH)
        self.confidence_threshold = 60  # Lower threshold for coaching
    
    @property
    def capabilities(self) -> list[str]:
        return [
            "suggest_improvements",
            "generate_action_plan",
            "explain_factors",
            "offer_encouragement",
        ]
    
    async def execute(
        self,
        action: str,
        context: AgentContext,
        parameters: dict[str, Any],
    ) -> AgentDecision:
        if action == "suggest_improvements":
            return await self._suggest_improvements(context)
        elif action == "generate_action_plan":
            return await self._generate_action_plan(context, parameters)
        elif action == "explain_factors":
            return await self._explain_factors(context)
        elif action == "offer_encouragement":
            return await self._offer_encouragement(context)
        else:
            return self._create_decision(
                "error",
                f"Unknown action: {action}",
                0,
                "Action not supported",
            )
    
    async def _suggest_improvements(self, context: AgentContext) -> AgentDecision:
        """
        Suggest actionable improvements based on reason codes.
        
        GUARDRAIL: All suggestions are directional, no promises.
        """
        scenarios = context.scenarios or []
        
        # Collect reason codes from non-eligible scenarios
        reason_code_map = {
            "RC001": {
                "factor": "Credit history length",
                "suggestion": "Consider becoming an authorized user on a family member's older account",
                "timeframe": "3-6 months to see impact",
            },
            "RC002": {
                "factor": "Credit score",
                "suggestion": "Focus on paying all bills on time and reducing credit utilization below 30%",
                "timeframe": "2-6 months for score improvement",
            },
            "RC003": {
                "factor": "Debt-to-income ratio",
                "suggestion": "Consider paying down existing debt before applying",
                "timeframe": "Depends on debt amount",
            },
            "RC004": {
                "factor": "Income documentation",
                "suggestion": "Gather additional income documents (pay stubs, tax returns, bank statements)",
                "timeframe": "Immediate action possible",
            },
            "RC005": {
                "factor": "Employment stability",
                "suggestion": "If recently employed, wait 3-6 months to build employment history",
                "timeframe": "3-6 months",
            },
            "RC006": {
                "factor": "Credit utilization",
                "suggestion": "Pay down credit card balances to below 30% of limit",
                "timeframe": "1-2 billing cycles",
            },
        }
        
        suggestions = []
        for scenario in scenarios:
            if scenario.get("status") != "eligible":
                for code in scenario.get("reason_codes", []):
                    if code in reason_code_map and code not in [s.get("code") for s in suggestions]:
                        info = reason_code_map[code]
                        suggestions.append({
                            "code": code,
                            "factor": info["factor"],
                            "suggestion": info["suggestion"],
                            "timeframe": info["timeframe"],
                        })
        
        if not suggestions:
            return self._create_decision(
                "coaching",
                "Continue monitoring your financial profile",
                75,
                "No specific improvements identified at this time",
            )
        
        # Format top 3 suggestions
        top_suggestions = suggestions[:3]
        formatted = "; ".join([
            f"{s['factor']}: {s['suggestion']} ({s['timeframe']})"
            for s in top_suggestions
        ])
        
        return self._create_decision(
            "improvements",
            f"Top focus areas: {formatted}",
            80,
            f"Based on analysis of {len(scenarios)} program(s). These are directional suggestions, not guarantees.",
        )
    
    async def _generate_action_plan(
        self,
        context: AgentContext,
        parameters: dict[str, Any],
    ) -> AgentDecision:
        """
        Generate a prioritized action plan.
        
        GUARDRAIL: Plan is advisory only, no outcome promises.
        """
        timeframe = parameters.get("timeframe_months", 6)
        scenarios = context.scenarios or []
        
        # Analyze what's closest to eligibility
        refer_scenarios = [s for s in scenarios if s.get("status") == "refer"]
        
        if not refer_scenarios and not scenarios:
            return self._create_decision(
                "action_plan",
                "Complete your intake form first to receive personalized guidance",
                70,
                "Need scenario data to generate action plan",
            )
        
        # Build action plan phases
        immediate_actions = []
        short_term_actions = []
        medium_term_actions = []
        
        # Check for quick wins
        intake = context.intake_data
        
        if intake.get("credit_utilization", 100) > 30:
            immediate_actions.append("Pay down credit card balances to under 30% utilization")
        
        if not intake.get("bank_account_linked"):
            immediate_actions.append("Link bank account for cash flow verification")
        
        # Short-term based on reason codes
        reason_codes = set()
        for s in scenarios:
            reason_codes.update(s.get("reason_codes", []))
        
        if "RC002" in reason_codes:
            short_term_actions.append("Set up autopay for all bills to build payment history")
        
        if "RC003" in reason_codes:
            short_term_actions.append("Focus on debt paydown - highest interest first")
        
        # Medium-term goals
        if refer_scenarios:
            medium_term_actions.append(f"Re-apply after addressing verification items for {len(refer_scenarios)} program(s)")
        
        plan = {
            "immediate": immediate_actions or ["No immediate actions needed"],
            "30_day": short_term_actions or ["Continue current financial habits"],
            "90_day": medium_term_actions or ["Monitor for new program opportunities"],
        }
        
        return self._create_decision(
            "action_plan",
            f"Action plan generated: {len(immediate_actions)} immediate, {len(short_term_actions)} short-term, {len(medium_term_actions)} medium-term actions",
            75,
            f"Plan tailored for {timeframe}-month horizon. Results may vary based on individual circumstances.",
        )
    
    async def _explain_factors(self, context: AgentContext) -> AgentDecision:
        """Explain what factors affect eligibility."""
        factors_explanation = [
            "Credit score: Impacts rate and eligibility across most programs",
            "Debt-to-income: Monthly debt payments vs monthly income",
            "Employment history: Stability matters for many lenders",
            "Credit utilization: Keeping balances low shows responsible use",
            "Payment history: On-time payments are crucial",
        ]
        
        return self._create_decision(
            "education",
            "Key factors: " + "; ".join(factors_explanation[:3]),
            90,
            "General credit factors that impact most lending decisions",
        )
    
    async def _offer_encouragement(self, context: AgentContext) -> AgentDecision:
        """Offer appropriate encouragement based on situation."""
        scenarios = context.scenarios or []
        
        eligible = [s for s in scenarios if s.get("status") == "eligible"]
        refer = [s for s in scenarios if s.get("status") == "refer"]
        
        if eligible:
            return self._create_decision(
                "encouragement",
                f"Great news! You have {len(eligible)} option(s) available to explore",
                95,
                "Consumer has qualifying options",
            )
        elif refer:
            return self._create_decision(
                "encouragement",
                f"You're close! {len(refer)} program(s) are possible with additional verification",
                80,
                "Consumer is near eligibility for some programs",
            )
        else:
            return self._create_decision(
                "encouragement",
                "Every financial journey has a starting point. Let's focus on building toward your goals",
                70,
                "Consumer may need time to build profile",
            )


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflows for GOATCRD.
    
    Manages agent execution, inter-agent communication,
    and human-in-the-loop escalation.
    """
    
    def __init__(self):
        self.agents: dict[AgentRole, BaseAgent] = {
            AgentRole.INTAKE_SPECIALIST: IntakeSpecialist(),
            AgentRole.SCENARIO_ANALYST: ScenarioAnalyst(),
            AgentRole.COMPLIANCE_REVIEWER: ComplianceReviewer(),
        }
        self.task_queue: list[AgentTask] = []
        self.completed_tasks: dict[UUID, AgentTask] = {}
        self.decisions: list[AgentDecision] = []
    
    async def run_workflow(
        self,
        workflow_name: str,
        context: AgentContext,
    ) -> list[AgentDecision]:
        """
        Run a predefined workflow.
        
        Workflows define sequences of agent tasks.
        """
        if workflow_name == "intake_review":
            return await self._workflow_intake_review(context)
        elif workflow_name == "scenario_analysis":
            return await self._workflow_scenario_analysis(context)
        elif workflow_name == "full_evaluation":
            return await self._workflow_full_evaluation(context)
        else:
            raise ValueError(f"Unknown workflow: {workflow_name}")
    
    async def execute_task(
        self,
        task: AgentTask,
        context: AgentContext,
    ) -> AgentDecision:
        """Execute a single agent task."""
        agent = self.agents.get(task.agent_role)
        if not agent:
            raise ValueError(f"No agent for role: {task.agent_role}")
        
        task.status = AgentStatus.RUNNING
        task.started_at = datetime.now(timezone.utc)
        
        try:
            decision = await agent.execute(
                task.action,
                context,
                task.parameters,
            )
            
            task.status = AgentStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.result = decision
            
            self.decisions.append(decision)
            self.completed_tasks[task.task_id] = task
            
            return decision
            
        except Exception as e:
            task.status = AgentStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            task.error = str(e)
            raise
    
    async def _workflow_intake_review(
        self,
        context: AgentContext,
    ) -> list[AgentDecision]:
        """Workflow for intake review."""
        decisions = []
        
        # Task 1: Validate intake
        task1 = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.INTAKE_SPECIALIST,
            action="validate_intake",
            parameters={},
        )
        decisions.append(await self.execute_task(task1, context))
        
        # Task 2: Detect inconsistencies
        task2 = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.INTAKE_SPECIALIST,
            action="detect_inconsistencies",
            parameters={},
        )
        decisions.append(await self.execute_task(task2, context))
        
        # Task 3: Suggest missing fields
        task3 = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.INTAKE_SPECIALIST,
            action="suggest_missing_fields",
            parameters={},
        )
        decisions.append(await self.execute_task(task3, context))
        
        return decisions
    
    async def _workflow_scenario_analysis(
        self,
        context: AgentContext,
    ) -> list[AgentDecision]:
        """Workflow for scenario analysis."""
        decisions = []
        
        # Task 1: Analyze scenarios
        task1 = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.SCENARIO_ANALYST,
            action="analyze_scenarios",
            parameters={},
        )
        decisions.append(await self.execute_task(task1, context))
        
        # Task 2: Identify improvements
        task2 = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.SCENARIO_ANALYST,
            action="identify_improvements",
            parameters={},
        )
        decisions.append(await self.execute_task(task2, context))
        
        # Task 3: Compliance review
        task3 = AgentTask(
            task_id=uuid4(),
            agent_role=AgentRole.COMPLIANCE_REVIEWER,
            action="review_adverse_action",
            parameters={},
        )
        decisions.append(await self.execute_task(task3, context))
        
        return decisions
    
    async def _workflow_full_evaluation(
        self,
        context: AgentContext,
    ) -> list[AgentDecision]:
        """Full evaluation workflow combining intake and scenario analysis."""
        decisions = []
        
        # Intake review
        decisions.extend(await self._workflow_intake_review(context))
        
        # Scenario analysis (if intake is valid)
        intake_valid = all(d.confidence >= 70 for d in decisions if d.decision_type == "validation")
        
        if intake_valid and context.scenarios:
            decisions.extend(await self._workflow_scenario_analysis(context))
        
        return decisions
    
    def get_human_review_required(self) -> list[AgentDecision]:
        """Get all decisions requiring human review."""
        return [d for d in self.decisions if d.requires_human_review]
    
    def clear_session(self):
        """Clear session state."""
        self.task_queue.clear()
        self.completed_tasks.clear()
        self.decisions.clear()


# Factory function
def create_orchestrator() -> AgentOrchestrator:
    """Create a new agent orchestrator."""
    return AgentOrchestrator()
