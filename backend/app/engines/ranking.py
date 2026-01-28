"""
GOATCRD Ranking Engine
Multi-mode scenario ranking with gating and tie-breakers
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any

from app.engines.scenario_builder import ScenarioResult
from app.models import EligibilityStatus


class RankingMode(str, Enum):
    """Ranking modes per GOATCRD spec."""
    
    LOWEST_PAYMENT = "lowest_payment"
    LOWEST_TOTAL_COST = "lowest_total_cost"
    FASTEST_CLOSE = "fastest_close"
    HIGHEST_CERTAINTY = "highest_certainty"
    BEST_GOAL_FIT = "best_goal_fit"


@dataclass
class RankedScenario:
    """Scenario with ranking information."""
    
    scenario: ScenarioResult
    rank: int
    score: float
    gated: bool
    gating_reason: str | None = None


@dataclass
class RankingResult:
    """Complete ranking result for a mode."""
    
    mode: RankingMode
    ranked_scenarios: list[RankedScenario]
    gated_scenarios: list[RankedScenario]
    sensitivity_notes: list[str]


class RankingEngine:
    """
    Multi-mode ranking engine with gating and tie-breakers.
    
    Ranking Modes:
    - lowest_payment: Sort by monthly payment
    - lowest_total_cost: Sort by total cost over term
    - fastest_close: Sort by time to close
    - highest_certainty: Sort by confidence score
    - best_goal_fit: Sort by goal alignment (requires consumer goals)
    
    Gating:
    - Pricing confidence < 50 for payment/cost modes
    - Missing docs for fastest_close
    """
    
    def __init__(
        self,
        pricing_confidence_threshold: int = 50,
        equivalence_threshold: float = 0.05,
    ):
        self.pricing_confidence_threshold = pricing_confidence_threshold
        self.equivalence_threshold = equivalence_threshold
    
    def rank(
        self,
        scenarios: list[ScenarioResult],
        mode: RankingMode,
        consumer_goals: dict[str, Any] | None = None,
    ) -> RankingResult:
        """
        Rank scenarios in specified mode.
        
        Args:
            scenarios: List of scenarios to rank
            mode: Ranking mode
            consumer_goals: Optional consumer goals for goal_fit mode
        
        Returns:
            RankingResult with ranked and gated scenarios
        """
        # Filter to ELIGIBLE only for ranking
        eligible = [s for s in scenarios if s.status == EligibilityStatus.ELIGIBLE]
        
        # Apply gating
        ranked: list[RankedScenario] = []
        gated: list[RankedScenario] = []
        
        for scenario in eligible:
            gated_result = self._check_gating(scenario, mode)
            if gated_result:
                gated.append(RankedScenario(
                    scenario=scenario,
                    rank=0,
                    score=0,
                    gated=True,
                    gating_reason=gated_result,
                ))
            else:
                score = self._calculate_score(scenario, mode, consumer_goals)
                ranked.append(RankedScenario(
                    scenario=scenario,
                    rank=0,
                    score=score,
                    gated=False,
                ))
        
        # Sort by score (with tie-breakers)
        ranked = self._apply_sort_and_tiebreakers(ranked, mode)
        
        # Assign ranks
        for i, rs in enumerate(ranked):
            rs.rank = i + 1
        
        # Generate sensitivity notes
        sensitivity_notes = self._generate_sensitivity_notes(ranked, mode)
        
        return RankingResult(
            mode=mode,
            ranked_scenarios=ranked,
            gated_scenarios=gated,
            sensitivity_notes=sensitivity_notes,
        )
    
    def _check_gating(
        self,
        scenario: ScenarioResult,
        mode: RankingMode,
    ) -> str | None:
        """
        Check if scenario should be gated from ranking.
        
        Returns gating reason if gated, None otherwise.
        """
        # Payment/cost modes require pricing confidence
        if mode in (RankingMode.LOWEST_PAYMENT, RankingMode.LOWEST_TOTAL_COST):
            if not scenario.pricing:
                return "Pricing not available"
            
            pricing_confidence = scenario.pricing.get("confidence", 0)
            if pricing_confidence < self.pricing_confidence_threshold:
                return f"Pricing confidence ({pricing_confidence}%) below threshold"
        
        # Fastest close requires doc completeness
        if mode == RankingMode.FASTEST_CLOSE:
            if len(scenario.verify_checklist) > 3:
                return "Too many verification items pending"
        
        return None
    
    def _calculate_score(
        self,
        scenario: ScenarioResult,
        mode: RankingMode,
        consumer_goals: dict[str, Any] | None = None,
    ) -> float:
        """Calculate ranking score for scenario in given mode."""
        
        if mode == RankingMode.LOWEST_PAYMENT:
            if scenario.pricing:
                # Lower is better, so negate for sorting
                return -scenario.pricing.get("monthly_payment", float("inf"))
            return float("-inf")
        
        elif mode == RankingMode.LOWEST_TOTAL_COST:
            if scenario.pricing:
                return -scenario.pricing.get("total_cost", float("inf"))
            return float("-inf")
        
        elif mode == RankingMode.FASTEST_CLOSE:
            # Fewer verify items = faster close
            return -len(scenario.verify_checklist)
        
        elif mode == RankingMode.HIGHEST_CERTAINTY:
            return scenario.confidence_score
        
        elif mode == RankingMode.BEST_GOAL_FIT:
            return self._calculate_goal_fit(scenario, consumer_goals)
        
        return 0
    
    def _calculate_goal_fit(
        self,
        scenario: ScenarioResult,
        goals: dict[str, Any] | None,
    ) -> float:
        """Calculate goal alignment score."""
        if not goals:
            return scenario.confidence_score  # Fallback to certainty
        
        score = 0.0
        
        # Speed priority
        if goals.get("priority_speed"):
            score += (10 - len(scenario.verify_checklist)) * 10
        
        # Cost priority
        if goals.get("priority_low_cost") and scenario.pricing:
            # Normalize to 0-100 scale
            total_cost = scenario.pricing.get("total_cost", 100000)
            score += max(0, 100 - (total_cost / 1000))
        
        # Certainty priority
        if goals.get("priority_certainty"):
            score += scenario.confidence_score
        
        return score
    
    def _apply_sort_and_tiebreakers(
        self,
        ranked: list[RankedScenario],
        mode: RankingMode,
    ) -> list[RankedScenario]:
        """Sort scenarios with tie-breakers."""
        
        def sort_key(rs: RankedScenario) -> tuple:
            scenario = rs.scenario
            
            # Primary: score (higher is better, we negated where needed)
            primary = rs.score
            
            # Tie-breaker 1: Confidence (higher is better)
            tb1 = scenario.confidence_score
            
            # Tie-breaker 2: Fewer verify items (lower is better)
            tb2 = -len(scenario.verify_checklist)
            
            # Tie-breaker 3: Fewer missing inputs (lower is better)
            tb3 = -len(scenario.missing_inputs)
            
            return (primary, tb1, tb2, tb3)
        
        return sorted(ranked, key=sort_key, reverse=True)
    
    def _generate_sensitivity_notes(
        self,
        ranked: list[RankedScenario],
        mode: RankingMode,
    ) -> list[str]:
        """Generate sensitivity notes about near-equivalent options."""
        notes = []
        
        if len(ranked) < 2:
            return notes
        
        # Check if top scenarios are within equivalence threshold
        top_score = ranked[0].score
        
        near_equivalent = []
        for rs in ranked[1:5]:  # Check top 5
            if top_score != 0:
                diff = abs(rs.score - top_score) / abs(top_score)
            else:
                diff = abs(rs.score - top_score)
            
            if diff <= self.equivalence_threshold:
                near_equivalent.append(rs)
        
        if near_equivalent:
            note = (
                f"Top {len(near_equivalent) + 1} options are within "
                f"{self.equivalence_threshold * 100:.0f}% on {mode.value}. "
                "Consider other factors like provider reputation or terms."
            )
            notes.append(note)
        
        # Add mode-specific notes
        if mode == RankingMode.LOWEST_PAYMENT:
            notes.append(
                "Lower monthly payments may result in higher total cost "
                "if the loan term is longer."
            )
        
        return notes
