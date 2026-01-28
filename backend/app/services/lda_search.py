"""
Less Discriminatory Alternative (LDA) Search Service
S4.4 - Automated search for fair alternatives to policies
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from enum import Enum
import random


class SearchStatus(str, Enum):
    """Status of an LDA search."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class PolicyAlternative:
    """A potential less discriminatory alternative."""
    
    alternative_id: UUID
    policy_field: str
    original_value: Any
    suggested_value: Any
    
    # Impact metrics
    disparate_impact_before: float
    disparate_impact_after: float
    approval_rate_change: float
    
    # Risk assessment
    business_impact: str  # "low", "medium", "high"
    implementation_effort: str  # "low", "medium", "high"
    
    rationale: str


@dataclass
class LDASearch:
    """An LDA search operation."""
    
    search_id: UUID
    program_id: UUID
    policy_rules: list[dict[str, Any]]
    protected_attribute: str
    
    # Results
    status: SearchStatus = SearchStatus.PENDING
    alternatives: list[PolicyAlternative] = field(default_factory=list)
    best_alternative: UUID | None = None
    
    # Metrics
    original_di_ratio: float = 0.0
    best_di_ratio: float = 0.0
    
    # Tracking
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error_message: str | None = None


class LDASearchService:
    """
    Automated search for Less Discriminatory Alternatives.
    
    Implements the CFPB model:
    1. Identify policies with potential disparate impact
    2. Search for alternatives that reduce impact
    3. Validate alternatives maintain business objectives
    """
    
    def __init__(self):
        self.searches: dict[UUID, LDASearch] = {}
    
    def create_search(
        self,
        program_id: UUID,
        policy_rules: list[dict[str, Any]],
        protected_attribute: str,
    ) -> LDASearch:
        """Create a new LDA search."""
        
        search = LDASearch(
            search_id=uuid4(),
            program_id=program_id,
            policy_rules=policy_rules,
            protected_attribute=protected_attribute,
        )
        
        self.searches[search.search_id] = search
        return search
    
    async def run_search(self, search_id: UUID) -> LDASearch:
        """
        Execute an LDA search.
        
        This simulates the search process. In production, this would:
        1. Run Monte Carlo simulations
        2. Use optimization algorithms
        3. Test against historical data
        """
        search = self.searches.get(search_id)
        if not search:
            raise ValueError("Search not found")
        
        search.status = SearchStatus.RUNNING
        search.started_at = datetime.now(timezone.utc)
        
        try:
            # Simulate search (in production, this would be real analysis)
            alternatives = await self._simulate_alternatives(search)
            
            search.alternatives = alternatives
            search.status = SearchStatus.COMPLETED
            search.completed_at = datetime.now(timezone.utc)
            
            # Calculate metrics
            if alternatives:
                search.original_di_ratio = alternatives[0].disparate_impact_before
                best = max(alternatives, key=lambda a: a.disparate_impact_after)
                search.best_alternative = best.alternative_id
                search.best_di_ratio = best.disparate_impact_after
            
        except Exception as e:
            search.status = SearchStatus.FAILED
            search.error_message = str(e)
        
        return search
    
    async def _simulate_alternatives(
        self,
        search: LDASearch,
    ) -> list[PolicyAlternative]:
        """Simulate finding alternatives (mock implementation)."""
        alternatives = []
        
        # Analyze each rule for potential alternatives
        for rule in search.policy_rules:
            rule_id = rule.get("id", rule.get("name", "unknown"))
            field = rule.get("field", "unknown")
            threshold = rule.get("threshold", rule.get("value", 0))
            
            if not isinstance(threshold, (int, float)):
                continue
            
            # Generate potential alternatives
            base_di = 0.70 + random.random() * 0.15
            
            # Try relaxing the threshold
            relaxed_threshold = threshold * 1.1 if threshold > 0 else threshold * 0.9
            relaxed_di = base_di + random.random() * 0.15
            
            alternatives.append(PolicyAlternative(
                alternative_id=uuid4(),
                policy_field=f"{rule_id}.{field}",
                original_value=threshold,
                suggested_value=round(relaxed_threshold, 2),
                disparate_impact_before=round(base_di, 3),
                disparate_impact_after=round(relaxed_di, 3),
                approval_rate_change=round(random.uniform(-0.02, 0.05), 3),
                business_impact="low" if abs(relaxed_threshold - threshold) < threshold * 0.05 else "medium",
                implementation_effort="low",
                rationale=f"Relaxing {field} threshold improves DI ratio with minimal business impact",
            ))
            
            # Try alternative criteria
            alt_di = base_di + random.random() * 0.2
            alternatives.append(PolicyAlternative(
                alternative_id=uuid4(),
                policy_field=f"{rule_id}.alternative_criteria",
                original_value=field,
                suggested_value=f"{field}_alternative",
                disparate_impact_before=round(base_di, 3),
                disparate_impact_after=round(alt_di, 3),
                approval_rate_change=round(random.uniform(-0.01, 0.03), 3),
                business_impact="medium",
                implementation_effort="medium",
                rationale=f"Using alternative criteria for {field} reduces disparate impact",
            ))
        
        # Sort by improvement
        alternatives.sort(
            key=lambda a: a.disparate_impact_after - a.disparate_impact_before,
            reverse=True
        )
        
        return alternatives[:10]  # Return top 10
    
    def get_search(self, search_id: UUID) -> LDASearch | None:
        """Get a search by ID."""
        return self.searches.get(search_id)
    
    def get_searches(
        self,
        program_id: UUID | None = None,
        status: SearchStatus | None = None,
        limit: int = 20,
    ) -> list[LDASearch]:
        """Get LDA searches with optional filters."""
        searches = list(self.searches.values())
        
        if program_id:
            searches = [s for s in searches if s.program_id == program_id]
        
        if status:
            searches = [s for s in searches if s.status == status]
        
        return sorted(
            searches,
            key=lambda s: s.started_at or s.search_id,
            reverse=True
        )[:limit]
    
    def export_search_results(self, search_id: UUID) -> dict[str, Any] | None:
        """Export search results as JSON."""
        search = self.get_search(search_id)
        if not search:
            return None
        
        return {
            "search_id": str(search.search_id),
            "program_id": str(search.program_id),
            "protected_attribute": search.protected_attribute,
            "status": search.status.value,
            "original_di_ratio": search.original_di_ratio,
            "best_di_ratio": search.best_di_ratio,
            "improvement": round(search.best_di_ratio - search.original_di_ratio, 3) if search.best_di_ratio else 0,
            "alternatives_count": len(search.alternatives),
            "best_alternative": str(search.best_alternative) if search.best_alternative else None,
            "alternatives": [
                {
                    "id": str(a.alternative_id),
                    "field": a.policy_field,
                    "original": a.original_value,
                    "suggested": a.suggested_value,
                    "di_improvement": round(a.disparate_impact_after - a.disparate_impact_before, 3),
                    "business_impact": a.business_impact,
                    "rationale": a.rationale,
                }
                for a in search.alternatives
            ],
        }


# Singleton instance
lda_search = LDASearchService()
