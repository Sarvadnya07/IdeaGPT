"""
Shared AI generation glue.

Every AI generation path (startup evaluation, roadmap, PRD, pitch deck, labs,
background AI tasks) needs the same three cross-cutting steps:

  1. Parse a provider response into a JSON object, tolerating markdown fences
     and stray prose around the payload.
  2. Build the deterministic-engine fallback payload when the provider path
     fails, so core functionality survives a total external AI outage.
  3. Tag a payload with execution provenance (real provider vs deterministic
     vs cached) that the frontend and the AI artifact service consume.

Historically each of these was re-implemented inline in the orchestrator, the
evaluation executor, and individual adapters. Centralising them here means
repair and fallback semantics change in exactly one place.
"""

import json
import logging
from typing import Any, Dict, Optional

from app.ai.validators.output_validator import OutputValidator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Execution provenance markers (consumed by the frontend + AIArtifactService).
# ---------------------------------------------------------------------------
EXECUTION_TYPE_REAL_PROVIDER = "REAL_PROVIDER"
EXECUTION_TYPE_DETERMINISTIC = "DETERMINISTIC_ENGINE"
EXECUTION_TYPE_CACHED = "CACHED_RESULT"

# Identifier reported as the provider/model when the deterministic engine runs.
DETERMINISTIC_PROVIDER = "deterministic-engine-v2.6"
DETERMINISTIC_MODEL = "rule-based-v2.6"

# Providers that explicitly request the offline deterministic engine.
DETERMINISTIC_PROVIDER_ALIASES = frozenset(
    {"deterministic", "rule-based", DETERMINISTIC_PROVIDER}
)


def is_deterministic_provider(provider: Optional[str]) -> bool:
    """True when the caller explicitly requested the offline engine."""
    return (provider or "").strip().lower() in DETERMINISTIC_PROVIDER_ALIASES


def parse_provider_json(raw: Any) -> Optional[Dict[str, Any]]:
    """
    Normalise a provider response into a JSON object, or return None.

    Accepts either an already-decoded dict or raw text. Text is cleaned with
    OutputValidator.clean_json_string (which strips ```json fences and
    surrounding prose) before parsing.
    """
    if isinstance(raw, dict):
        return raw

    if not isinstance(raw, str):
        return None

    try:
        parsed = json.loads(OutputValidator.clean_json_string(raw))
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.debug("Provider payload was not valid JSON: %s", exc)
        return None

    return parsed if isinstance(parsed, dict) else None


def read_execution_provenance(payload: Any) -> tuple[str, bool]:
    """
    Read the (execution_type, fallback_used) pair from a generated payload.

    Used by route handlers that must persist provenance onto an AI artifact.
    Defaults to REAL_PROVIDER/False so a payload lacking markers is never
    misreported as a deterministic fallback.
    """
    if not isinstance(payload, dict):
        return EXECUTION_TYPE_REAL_PROVIDER, False
    return (
        payload.get("_execution_type", EXECUTION_TYPE_REAL_PROVIDER),
        bool(payload.get("_fallback_used", False)),
    )


def tag_execution(
    payload: Dict[str, Any],
    execution_type: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    fallback_used: bool = False,
    fallback_reason: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Attach execution provenance to a result payload in place, and return it.

    These keys are additive: existing payload fields (score, dimensions, etc.)
    are never overwritten, so callers can keep their domain shape intact.
    """
    payload["_execution_type"] = execution_type
    payload["_fallback_used"] = fallback_used
    if provider is not None:
        payload["_provider"] = provider
    if model is not None:
        payload["_model"] = model
    if fallback_reason is not None:
        payload["_fallback_reason"] = fallback_reason
    return payload


class DeterministicFallback:
    """
    Builds offline deterministic-engine payloads.

    This is the single supported way to fall back to the deterministic engine.
    Keeping it here (rather than importing DeterministicEvaluationEngine from
    arbitrary call sites) preserves the engine's purity and makes the fallback
    policy auditable.
    """

    ENGINE_VERSION = DETERMINISTIC_PROVIDER

    @staticmethod
    def from_idea(idea: Any) -> Dict[str, Any]:
        """Evaluate a real Idea ORM instance with the deterministic engine."""
        from app.evaluation.engine import DeterministicEvaluationEngine

        payload: Dict[str, Any] = DeterministicEvaluationEngine.evaluate(idea)
        payload.setdefault("metadata", {})
        return payload

    @staticmethod
    def snapshot_object(snapshot: Dict[str, Any]) -> Any:
        """
        Build a detached, attribute-compatible stand-in for an Idea row.

        Shared by from_idea_snapshot() and by the orchestrator's internal fallback
        (PRODUCT-01 P-07) so both paths evaluate the *same* inputs. When a caller
        cannot hand the orchestrator the ORM instance (because the session was
        closed to avoid holding a connection across the LLM call), it hands this
        snapshot dict instead and fallback fidelity is preserved.
        """
        return type(
            "IdeaSnapshotObj",
            (),
            {
                "title": snapshot.get("title", ""),
                "problem_statement": snapshot.get("problem_statement", ""),
                "solution_description": snapshot.get("solution_description", ""),
                "target_users": snapshot.get("target_users", ""),
                "industry": snapshot.get("industry", ""),
                "business_model": snapshot.get("business_model", ""),
                "stage": snapshot.get("stage", ""),
                "tags": snapshot.get("tags", ""),
                "notes": snapshot.get("notes", ""),
            },
        )()

    @classmethod
    def from_idea_snapshot(cls, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a detached idea snapshot dictionary with the deterministic engine."""
        return cls.from_idea(cls.snapshot_object(snapshot))

    @staticmethod
    def from_prompt(prompt: str) -> Dict[str, Any]:
        """
        Build a deterministic payload from a bare prompt when no Idea row is
        available (e.g. health/experimental task paths).
        """
        from app.evaluation.engine import DeterministicEvaluationEngine

        text = (prompt or "Startup Idea").strip() or "Startup Idea"
        placeholder = type(
            "IdeaObj",
            (),
            {
                "title": text[:50],
                "problem_statement": text,
                "solution_description": text,
                "target_users": "Founders, Developers",
                "industry": "Technology",
                "business_model": "B2B SaaS",
                "stage": "Prototype",
                "tags": "ai, tech, saas",
                "notes": "",
            },
        )()
        payload: Dict[str, Any] = DeterministicEvaluationEngine.evaluate(placeholder)
        payload.setdefault("metadata", {})
        return payload

    @classmethod
    def build(
        cls, idea: Any = None, prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Evaluate an idea when present, otherwise derive one from the prompt."""
        if idea is not None:
            return cls.from_idea(idea)
        return cls.from_prompt(prompt or "")

    @staticmethod
    def with_reason(payload: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """
        Record why the deterministic engine ran. Truncated to keep error text
        bounded when it originates from an upstream provider exception.
        """
        payload.setdefault("metadata", {})
        payload["metadata"]["fallback_reason"] = (reason or "")[:200]
        return payload
