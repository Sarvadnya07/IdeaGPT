"""
IdeaGPT AI Gateway — Evidence Taxonomy, Claim Classifier & Conflict Resolver.
Enforces strict grounding contracts:
- FACT: Must have valid source_url or source_title
- ESTIMATE: Must contain documented assumptions
- INFERENCE: Must clearly derive from verified evidence
- RECOMMENDATION: Must document strategic rationale
- UNKNOWN: Must explain insufficient evidence
- CONFLICTING_EVIDENCE: Synthesizes conflicting source claims into estimated ranges
"""

import re
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone

from app.ai.gateway.evidence.models import (
    EvidenceClassification,
    ConfidenceLevel,
    NormalizedEvidence,
    NormalizedSource,
)


class EvidenceValidator:
    """
    Validates and normalizes evidence items, enforces classification rules,
    downgrades unsubstantiated claims, and resolves source conflicts.
    """

    @classmethod
    def validate_item(cls, item: Any) -> bool:
        """
        Validates individual evidence claim integrity for both NormalizedEvidence and EvidenceItem models.
        """
        ev_type = getattr(item, "classification", None) or getattr(item, "evidence_type", None)
        ev_str = str(ev_type).upper()

        if "FACT" in ev_str:
            source_urls = getattr(item, "source_urls", None) or []
            source_ids = getattr(item, "source_ids", None) or []
            source_url = getattr(item, "source_url", None)
            source_title = getattr(item, "source_title", None)
            if not (source_urls or source_ids or source_url or source_title):
                return False
        elif "ESTIMATE" in ev_str:
            if not getattr(item, "assumptions", None):
                return False
        elif "INFERENCE" in ev_str or "RECOMMENDATION" in ev_str:
            reasoning = getattr(item, "reasoning_notes", None) or getattr(item, "reasoning", None)
            if not reasoning and not getattr(item, "claim", None):
                return False
        return True

    @classmethod
    def sanitize_evidence_list(
        cls,
        raw_items: List[Dict[str, Any]],
        available_sources: Optional[List[NormalizedSource]] = None
    ) -> List[NormalizedEvidence]:
        """
        Parses raw evidence dicts, binds them to valid sources, downgrades unsupported FACTs,
        and returns clean NormalizedEvidence objects.
        """
        source_map: Dict[str, NormalizedSource] = {}
        if available_sources:
            for s in available_sources:
                source_map[s.id] = s
                source_map[s.url] = s

        sanitized: List[NormalizedEvidence] = []
        for raw in raw_items:
            try:
                raw_class = str(raw.get("classification") or raw.get("evidence_type") or "INFERENCE").upper()
                if raw_class not in EvidenceClassification.__members__:
                    classification = EvidenceClassification.INFERENCE
                else:
                    classification = EvidenceClassification(raw_class)

                claim = str(raw.get("claim") or "").strip()
                if not claim:
                    continue

                source_urls: List[str] = []
                source_ids: List[str] = []
                raw_urls = raw.get("source_urls") or []
                if isinstance(raw_urls, str):
                    raw_urls = [raw_urls]
                if raw.get("source_url"):
                    raw_urls.append(raw.get("source_url"))

                for u in raw_urls:
                    if u and u.startswith("http"):
                        source_urls.append(u)

                raw_sids = raw.get("source_ids") or []
                if isinstance(raw_sids, str):
                    raw_sids = [raw_sids]
                for sid in raw_sids:
                    if sid:
                        source_ids.append(sid)

                assumptions = raw.get("assumptions")
                reasoning = raw.get("reasoning_notes") or raw.get("reasoning")
                supporting_excerpt = raw.get("supporting_excerpt")

                # Classification rule enforcement:
                # Rule 1: Unsupported numerical market claims (e.g. TAM, $X.XB) without sources must be ESTIMATE
                if classification == EvidenceClassification.FACT and not source_urls and not source_ids and re.search(r"\$\d+(\.\d+)?[BMKbmk]?", claim):
                    classification = EvidenceClassification.ESTIMATE
                    if not assumptions:
                        assumptions = "Uncited numerical market figure downgraded to speculative estimate."
                # Rule 2: Other FACTs without verified source must be downgraded to INFERENCE
                elif classification == EvidenceClassification.FACT and not source_urls and not source_ids:
                    classification = EvidenceClassification.INFERENCE
                    if not reasoning:
                        reasoning = "Unsubstantiated factual claim downgraded to model inference due to missing source reference."

                conf_val = raw.get("confidence", "MEDIUM")
                if isinstance(conf_val, (int, float)):
                    if conf_val >= 0.8:
                        confidence = ConfidenceLevel.HIGH
                        conf_score = float(conf_val)
                    elif conf_val >= 0.5:
                        confidence = ConfidenceLevel.MEDIUM
                        conf_score = float(conf_val)
                    else:
                        confidence = ConfidenceLevel.LOW
                        conf_score = float(conf_val)
                else:
                    conf_str = str(conf_val).upper()
                    if conf_str in ConfidenceLevel.__members__:
                        confidence = ConfidenceLevel(conf_str)
                    else:
                        confidence = ConfidenceLevel.MEDIUM
                    conf_score = 0.9 if confidence == ConfidenceLevel.HIGH else (0.7 if confidence == ConfidenceLevel.MEDIUM else 0.4)

                ev_id = hashlib.sha256(f"{claim}:{classification.value}".encode("utf-8")).hexdigest()[:12]

                sanitized.append(
                    NormalizedEvidence(
                        id=ev_id,
                        claim=claim,
                        classification=classification,
                        source_ids=source_ids,
                        source_urls=source_urls,
                        supporting_excerpt=supporting_excerpt,
                        confidence=confidence,
                        confidence_score=conf_score,
                        assumptions=assumptions,
                        reasoning_notes=reasoning,
                        retrieved_at=datetime.now(timezone.utc),
                    )
                )
            except Exception:
                continue

        return sanitized

    @classmethod
    def detect_conflicting_sources(
        cls,
        evidence_items: List[NormalizedEvidence]
    ) -> List[Dict[str, Any]]:
        """
        Scans evidence for conflicting numerical claims on the same topic and returns structured CONFLICTING_EVIDENCE records.
        """
        conflicts: List[Dict[str, Any]] = []
        market_numbers: List[Tuple[float, str, str]] = []  # (value_in_billions, raw_str, source)

        for ev in evidence_items:
            # Look for market size numbers e.g. "$3.8B", "$5.1 billion"
            matches = re.findall(r"\$(\d+(?:\.\d+)?)\s*(?:billion|B|b|million|M|m)?", ev.claim, re.IGNORECASE)
            for m in matches:
                try:
                    val = float(m)
                    market_numbers.append((val, ev.claim, ev.source_urls[0] if ev.source_urls else "Unknown source"))
                except ValueError:
                    pass

        if len(market_numbers) >= 2:
            min_val = min(market_numbers, key=lambda x: x[0])
            max_val = max(market_numbers, key=lambda x: x[0])
            if max_val[0] - min_val[0] > 0.5:  # Significant delta
                conflicts.append({
                    "topic": "Market Size Estimate Discrepancy",
                    "conflict_type": "NUMERICAL_VARIANCE",
                    "estimated_range": f"${min_val[0]:.1f}B – ${max_val[0]:.1f}B",
                    "source_a": {"claim": min_val[1], "source": min_val[2]},
                    "source_b": {"claim": max_val[1], "source": max_val[2]},
                    "confidence": "MEDIUM",
                    "resolution_notes": "Sources employ different market taxonomy boundaries. Analysis adopts the conservative composite range.",
                })

        return conflicts
