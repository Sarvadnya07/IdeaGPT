"""
IdeaGPT Evidence Taxonomy and Validator.
Ensures factual claims, market sizes, competitor data, and inferences
are strictly tagged and substantiated.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.ai.gateway.models import EvidenceItem, EvidenceType


class EvidenceValidator:
    """
    Validates evidence items to prevent unsupported claims from being presented as verified facts.
    """

    @staticmethod
    def validate_item(item: EvidenceItem) -> bool:
        """
        Validates individual evidence claim integrity:
        - FACT: Must have valid source_url or source_title and retrieved_at
        - ESTIMATE: Must have stated assumptions
        - INFERENCE: Must have logical reasoning rationale
        - UNKNOWN: Represents explicitly unverifiable data
        """
        if item.evidence_type == EvidenceType.FACT:
            if not (item.source_url or item.source_title):
                # Cannot claim FACT without a verifiable source
                return False
        elif item.evidence_type == EvidenceType.ESTIMATE:
            if not item.assumptions:
                # Estimates must document assumptions
                return False
        elif item.evidence_type == EvidenceType.INFERENCE:
            if not item.reasoning and not item.claim:
                return False
        return True

    @staticmethod
    def sanitize_evidence_list(raw_items: List[Dict[str, Any]]) -> List[EvidenceItem]:
        """
        Parses and validates a list of raw evidence objects from LLM output.
        Downgrades unsupported FACT claims to INFERENCE or ESTIMATE if sources are missing.
        """
        sanitized: List[EvidenceItem] = []
        for raw in raw_items:
            try:
                ev_type_str = str(raw.get("evidence_type", "INFERENCE")).upper()
                if ev_type_str not in EvidenceType.__members__:
                    ev_type = EvidenceType.INFERENCE
                else:
                    ev_type = EvidenceType(ev_type_str)

                source_url = raw.get("source_url")
                source_title = raw.get("source_title")
                assumptions = raw.get("assumptions")
                reasoning = raw.get("reasoning")
                claim = raw.get("claim", "")
                value = raw.get("value")
                confidence = float(raw.get("confidence", 0.8))

                # Integrity check: If claim is labeled FACT but has no source, downgrade to INFERENCE
                if ev_type == EvidenceType.FACT and not (source_url or source_title):
                    ev_type = EvidenceType.INFERENCE
                    if not reasoning:
                        reasoning = "Unsubstantiated factual claim downgraded to model inference."

                item = EvidenceItem(
                    evidence_type=ev_type,
                    claim=claim,
                    value=value,
                    source_title=source_title,
                    source_url=source_url,
                    assumptions=assumptions,
                    reasoning=reasoning,
                    confidence=min(max(confidence, 0.0), 1.0),
                    retrieved_at=datetime.now(timezone.utc)
                )
                sanitized.append(item)
            except Exception:
                continue

        return sanitized
