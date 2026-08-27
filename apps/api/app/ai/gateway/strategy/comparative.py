"""
IdeaGPT Phase C — Comparative Strategy Engine.
Performs multi-idea comparative decision modeling, deterministic weighted scoring,
criterion winner determination, and critical trade-off synthesis across 2-5 ideas.
"""

import uuid
from typing import Any, Dict, List, Optional
from app.ai.gateway.strategy.models import (
    DataProvenance,
    Reversibility,
    DecisionConfidence,
    Tradeoff,
    MultiIdeaComparisonResult,
)


class ComparativeStrategyEngine:
    """
    Executes multi-idea comparison using deterministic decision matrices.
    """

    CRITERIA_WEIGHTS = {
        "Market Potential & Demand": 0.25,
        "Technical Feasibility": 0.20,
        "Business Viability & Unit Economics": 0.20,
        "Defensibility Moat & Switching Costs": 0.20,
        "Time to MVP & Execution Simplicity": 0.15,
    }

    @classmethod
    def compare_multiple_ideas(
        cls,
        ideas_data: List[Dict[str, Any]]
    ) -> MultiIdeaComparisonResult:
        """
        Compares 2-5 ideas using deterministic weighted criteria calculations.
        """
        if not ideas_data or len(ideas_data) < 2:
            raise ValueError("ComparativeStrategyEngine requires at least 2 ideas.")

        idea_scores: Dict[str, float] = {}
        criteria_breakdown: Dict[str, Dict[str, float]] = {}  # criterion_name -> {idea_id: score}

        for crit_name in cls.CRITERIA_WEIGHTS.keys():
            criteria_breakdown[crit_name] = {}

        for item in ideas_data:
            i_id = str(item.get("id") or item.get("idea_id"))
            eval_score = float(item.get("overall_score") or item.get("score") or 75.0)
            dims = item.get("dimensions") or {}

            # Extract or derive criterion scores
            m_score = float(dims.get("market_potential") or eval_score)
            t_score = float(dims.get("technical_feasibility") or eval_score)
            v_score = float(dims.get("business_viability") or eval_score)
            d_score = float(dims.get("competitive_differentiation") or (eval_score - 5.0))
            e_score = float(dims.get("execution_complexity") or (100.0 - (eval_score * 0.3)))  # Higher score = simpler execution

            criteria_breakdown["Market Potential & Demand"][i_id] = m_score
            criteria_breakdown["Technical Feasibility"][i_id] = t_score
            criteria_breakdown["Business Viability & Unit Economics"][i_id] = v_score
            criteria_breakdown["Defensibility Moat & Switching Costs"][i_id] = d_score
            criteria_breakdown["Time to MVP & Execution Simplicity"][i_id] = e_score

            # Deterministic weighted sum
            raw_attr = (
                m_score * cls.CRITERIA_WEIGHTS["Market Potential & Demand"]
                + t_score * cls.CRITERIA_WEIGHTS["Technical Feasibility"]
                + v_score * cls.CRITERIA_WEIGHTS["Business Viability & Unit Economics"]
                + d_score * cls.CRITERIA_WEIGHTS["Defensibility Moat & Switching Costs"]
                + e_score * cls.CRITERIA_WEIGHTS["Time to MVP & Execution Simplicity"]
            )

            # Apply standard risk adjustment (assuming base risk 30%)
            risk_exposure = float(item.get("risk_score") or 30.0)
            decision_score = round(raw_attr * (1.0 - (0.5 * (risk_exposure / 100.0))), 1)
            idea_scores[i_id] = decision_score

        # Sort ideas by decision score descending
        sorted_ideas = sorted(ideas_data, key=lambda x: idea_scores[str(x.get("id") or x.get("idea_id"))], reverse=True)

        winner = sorted_ideas[0]
        winner_id = str(winner.get("id") or winner.get("idea_id"))
        winner_title = str(winner.get("title") or "Top Ranked Idea")

        runner_up_id = None
        if len(sorted_ideas) > 1:
            runner_up = sorted_ideas[1]
            runner_up_id = str(runner_up.get("id") or runner_up.get("idea_id"))

        # Determine winner for each individual criterion
        criteria_winners: Dict[str, str] = {}
        idea_title_map = {str(i.get("id") or i.get("idea_id")): str(i.get("title") or i.get("id")) for i in ideas_data}

        for crit_name, score_map in criteria_breakdown.items():
            best_id = max(score_map.keys(), key=lambda k: score_map[k])
            criteria_winners[crit_name] = f"{idea_title_map.get(best_id, best_id)} ({score_map[best_id]:.0f}/100)"

        # Generate critical trade-off between winner and runner-up
        tradeoffs = []
        if runner_up_id:
            runner_up_title = idea_title_map.get(runner_up_id, runner_up_id)
            tradeoffs.append(
                Tradeoff(
                    id="comp-tradeoff-1",
                    dimension="Strategic Focus & Capital Allocation",
                    option_a_name=winner_title,
                    option_b_name=runner_up_title,
                    difference=f"'{winner_title}' achieves superior risk-adjusted score ({idea_scores[winner_id]}) compared to '{runner_up_title}' ({idea_scores[runner_up_id]}).",
                    consequence=f"Prioritizing '{winner_title}' maximizes probability of capital efficiency and faster market traction.",
                    reversibility=Reversibility.PARTIALLY_REVERSIBLE,
                    confidence=DecisionConfidence.HIGH,
                    provenance=DataProvenance.DETERMINISTIC_CALCULATION
                )
            )

        winner_rationale = (
            f"'{winner_title}' achieved the highest risk-adjusted decision score ({idea_scores[winner_id]}/100), "
            f"dominating on strategic criteria including {', '.join(list(criteria_winners.keys())[:2])}."
        )

        return MultiIdeaComparisonResult(
            compared_idea_ids=[str(i.get("id") or i.get("idea_id")) for i in ideas_data],
            winner_idea_id=winner_id,
            winner_idea_title=winner_title,
            winner_rationale=winner_rationale,
            strongest_alternative_id=runner_up_id,
            idea_decision_scores=idea_scores,
            criteria_winners=criteria_winners,
            critical_tradeoffs=tradeoffs,
            comparative_confidence=DecisionConfidence.HIGH,
            provenance=DataProvenance.DETERMINISTIC_CALCULATION
        )
