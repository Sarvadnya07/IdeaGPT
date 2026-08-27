"""
IdeaGPT AI Gateway — Deterministic Tool Policy & Budget Enforcement.
Enforces:
  1. Tool authorization & schema validation
  2. Least-privilege permission checks
  3. Strict finite budget limits (steps, calls, wall-clock, cost, recursion)
"""

from typing import Dict, Any, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime, timezone

class ToolBudget(BaseModel):
    max_steps: int = 5
    max_tool_calls: int = 8
    max_wall_clock_sec: float = 30.0
    max_tokens: int = 8192
    max_cost_usd: float = 0.50
    max_recursion_depth: int = 2

class ToolExecutionTracker(BaseModel):
    steps_taken: int = 0
    tool_calls_count: int = 0
    tokens_consumed: int = 0
    cost_incurred_usd: float = 0.0
    recursion_depth: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ToolPolicyException(Exception):
    """Raised when a tool execution violates security or budget limits."""
    pass

class ToolPolicyEngine:
    ALLOWED_TOOLS: Set[str] = {
        "web_search",
        "calculate_metrics",
        "extract_keywords",
        "validate_schema",
    }

    @classmethod
    def validate_tool_request(
        cls,
        tool_name: str,
        tool_args: Dict[str, Any],
        tracker: ToolExecutionTracker,
        budget: ToolBudget
    ) -> None:
        """
        Validates tool authorization and checks remaining budget allocations.
        """
        # 1. Tool Authorization Check
        if tool_name not in cls.ALLOWED_TOOLS:
            raise ToolPolicyException(f"Tool '{tool_name}' is not in the allowed tool registry.")

        # 2. Budget Steps Check
        if tracker.steps_taken >= budget.max_steps:
            raise ToolPolicyException(
                f"Exceeded max tool execution steps ({tracker.steps_taken} >= {budget.max_steps})."
            )

        # 3. Budget Call Count Check
        if tracker.tool_calls_count >= budget.max_tool_calls:
            raise ToolPolicyException(
                f"Exceeded max tool calls quota ({tracker.tool_calls_count} >= {budget.max_tool_calls})."
            )

        # 4. Recursion Depth Check
        if tracker.recursion_depth >= budget.max_recursion_depth:
            raise ToolPolicyException(
                f"Exceeded max tool recursion depth ({tracker.recursion_depth} >= {budget.max_recursion_depth})."
            )

        # 5. Wall Clock Check
        elapsed_sec = (datetime.now(timezone.utc) - tracker.started_at).total_seconds()
        if elapsed_sec > budget.max_wall_clock_sec:
            raise ToolPolicyException(
                f"Tool execution timed out ({elapsed_sec:.1f}s > {budget.max_wall_clock_sec}s)."
            )

        # 6. Cost Check
        if tracker.cost_incurred_usd >= budget.max_cost_usd:
            raise ToolPolicyException(
                f"Exceeded max tool cost budget (${tracker.cost_incurred_usd:.4f} >= ${budget.max_cost_usd:.2f})."
            )
