from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

from app.models.evaluation import Evaluation
from app.schemas.evaluation_schema import (
    DimensionDelta,
    ListDelta,
    SectionDelta,
    EvaluationProvenance,
    EvaluationVersionComparisonResponse,
)

HIGHER_IS_BETTER_METRICS = {
    "overall_score",
    "confidence",
    "innovation",
    "market_potential",
    "technical_feasibility",
    "business_viability",
    "scalability",
    "competitive_differentiation",
}

LOWER_IS_BETTER_METRICS = {
    "execution_complexity",
}

DIMENSION_LABELS: Dict[str, str] = {
    "innovation": "Innovation",
    "market_potential": "Market Potential",
    "technical_feasibility": "Technical Feasibility",
    "business_viability": "Business Viability",
    "scalability": "Scalability",
    "execution_complexity": "Execution Complexity",
    "competitive_differentiation": "Competitive Differentiation",
}


class EvaluationVersionComparisonService:
    """
    Pure, deterministic, read-only domain service for comparing two completed
    evaluation runs belonging to the same idea.
    
    Zero AI, zero database mutations, zero side-effects.
    """

    @staticmethod
    def _compute_numeric_delta(
        val_a: Optional[Any],
        val_b: Optional[Any],
        key: str,
        label: str,
    ) -> DimensionDelta:
        """
        Calculates exact signed decimal delta and semantic status without fabricating zeroes.
        """
        direction = "lower_is_better" if key in LOWER_IS_BETTER_METRICS else "higher_is_better"

        if val_a is None or val_b is None:
            float_a = float(val_a) if val_a is not None else None
            float_b = float(val_b) if val_b is not None else None
            return DimensionDelta(
                key=key,
                label=label,
                value_a=float_a,
                value_b=float_b,
                delta=None,
                formatted_delta=None,
                status="unavailable",
                direction=direction,
            )

        try:
            dec_a = Decimal(str(val_a))
            dec_b = Decimal(str(val_b))
        except Exception:
            return DimensionDelta(
                key=key,
                label=label,
                value_a=None,
                value_b=None,
                delta=None,
                formatted_delta=None,
                status="unavailable",
                direction=direction,
            )

        diff = dec_b - dec_a
        rounded_diff = diff.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        float_diff = float(rounded_diff)

        sign = "+" if rounded_diff > 0 else ""
        formatted_delta = f"{sign}{rounded_diff:.2f}"

        if rounded_diff == Decimal("0.00"):
            status = "unchanged"
        elif direction == "higher_is_better":
            status = "improved" if rounded_diff > 0 else "declined"
        else:
            status = "improved" if rounded_diff < 0 else "declined"

        return DimensionDelta(
            key=key,
            label=label,
            value_a=float(dec_a.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            value_b=float(dec_b.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            delta=float_diff,
            formatted_delta=formatted_delta,
            status=status,
            direction=direction,
        )

    @staticmethod
    def _compare_list(
        list_a: Optional[List[Any]],
        list_b: Optional[List[Any]],
    ) -> ListDelta:
        """
        Deterministically compares two text lists using case/whitespace normalization
        while preserving original display strings.
        """
        raw_a = [str(x).strip() for x in (list_a or []) if str(x).strip()]
        raw_b = [str(x).strip() for x in (list_b or []) if str(x).strip()]

        normalized_a: Dict[str, str] = {x.lower(): x for x in raw_a}
        normalized_b: Dict[str, str] = {x.lower(): x for x in raw_b}

        added = [orig for norm, orig in normalized_b.items() if norm not in normalized_a]
        removed = [orig for norm, orig in normalized_a.items() if norm not in normalized_b]
        retained = [orig for norm, orig in normalized_b.items() if norm in normalized_a]

        return ListDelta(
            added=added,
            removed=removed,
            retained=retained,
        )

    @staticmethod
    def _extract_provenance(ev: Evaluation) -> EvaluationProvenance:
        """
        Extracts execution and provenance metadata without exposing credentials or internal ORM state.
        """
        payload = ev.result_payload or {}
        meta = payload.get("metadata", {})

        provider = ev.provider or meta.get("provider")
        model = ev.model or meta.get("model")
        duration_ms = ev.duration_ms or meta.get("duration_ms")
        token_usage = ev.token_usage or meta.get("token_usage")
        estimated_cost = ev.estimated_cost or meta.get("estimated_cost")
        score = payload.get("score")

        return EvaluationProvenance(
            id=str(ev.id),
            created_at=ev.created_at.isoformat() if ev.created_at else None,
            completed_at=ev.completed_at.isoformat() if ev.completed_at else None,
            status=str(ev.status),
            provider=provider,
            model=model,
            duration_ms=duration_ms,
            token_usage=token_usage,
            estimated_cost=float(estimated_cost) if estimated_cost is not None else None,
            score=float(score) if score is not None else None,
        )

    @classmethod
    def compare_evaluation_versions(
        cls,
        eval_a: Evaluation,
        eval_b: Evaluation,
    ) -> EvaluationVersionComparisonResponse:
        """
        Compares two completed Evaluation records belonging to the same idea.
        """
        payload_a = eval_a.result_payload or {}
        payload_b = eval_b.result_payload or {}

        dims_a = payload_a.get("dimensions", {})
        dims_b = payload_b.get("dimensions", {})

        # 1. Overall Score & Confidence Delta
        overall_score = cls._compute_numeric_delta(
            payload_a.get("score"),
            payload_b.get("score"),
            "overall_score",
            "Overall Readiness Score",
        )

        conf_a = payload_a.get("confidence")
        conf_b = payload_b.get("confidence")
        confidence_delta = None
        if conf_a is not None or conf_b is not None:
            confidence_delta = cls._compute_numeric_delta(
                conf_a,
                conf_b,
                "confidence",
                "Evaluation Confidence",
            )

        # 2. Dimensions Comparison
        dimensions_list: List[DimensionDelta] = []
        for dim_key, dim_label in DIMENSION_LABELS.items():
            val_a = dims_a.get(dim_key) if isinstance(dims_a, dict) else None
            val_b = dims_b.get(dim_key) if isinstance(dims_b, dict) else None
            delta_obj = cls._compute_numeric_delta(val_a, val_b, dim_key, dim_label)
            dimensions_list.append(delta_obj)

        # 3. SWOT Lists Comparison
        swot_map: Dict[str, ListDelta] = {}

        # Strengths
        str_a = payload_a.get("strengths") or payload_a.get("swot", {}).get("strengths")
        str_b = payload_b.get("strengths") or payload_b.get("swot", {}).get("strengths")
        swot_map["strengths"] = cls._compare_list(str_a, str_b)

        # Weaknesses
        weak_a = payload_a.get("weaknesses") or payload_a.get("swot", {}).get("weaknesses")
        weak_b = payload_b.get("weaknesses") or payload_b.get("swot", {}).get("weaknesses")
        swot_map["weaknesses"] = cls._compare_list(weak_a, weak_b)

        # Opportunities
        opp_a = payload_a.get("opportunities") or payload_a.get("swot", {}).get("opportunities")
        opp_b = payload_b.get("opportunities") or payload_b.get("swot", {}).get("opportunities")
        swot_map["opportunities"] = cls._compare_list(opp_a, opp_b)

        # Threats
        threat_a = payload_a.get("threats") or payload_a.get("swot", {}).get("threats")
        threat_b = payload_b.get("threats") or payload_b.get("swot", {}).get("threats")
        swot_map["threats"] = cls._compare_list(threat_a, threat_b)

        # Recommendations
        rec_a = payload_a.get("recommendations")
        rec_b = payload_b.get("recommendations")
        swot_map["recommendations"] = cls._compare_list(rec_a, rec_b)

        # 4. Sections Comparison
        sections: List[SectionDelta] = []
        candidate_sections = [
            ("architecture_breakdown", "Technical Architecture"),
            ("market_fit", "Market Fit Analysis"),
            ("financial_projections", "Financial Projections"),
            ("risks", "Risk Assessment"),
        ]

        for sec_key, sec_label in candidate_sections:
            val_a = payload_a.get(sec_key)
            val_b = payload_b.get(sec_key)
            pres_a = bool(val_a)
            pres_b = bool(val_b)

            if not pres_a and not pres_b:
                status = "unavailable"
                diff_sum = "Section absent in both evaluations."
            elif not pres_a and pres_b:
                status = "added"
                diff_sum = "Section added in new evaluation version."
            elif pres_a and not pres_b:
                status = "removed"
                diff_sum = "Section removed in new evaluation version."
            elif val_a == val_b:
                status = "unchanged"
                diff_sum = "Section content identical across versions."
            else:
                status = "changed"
                diff_sum = "Section content updated across versions."

            sections.append(
                SectionDelta(
                    section_key=sec_key,
                    label=sec_label,
                    present_in_a=pres_a,
                    present_in_b=pres_b,
                    status=status,
                    diff_summary=diff_sum,
                    value_a=val_a if pres_a else None,
                    value_b=val_b if pres_b else None,
                )
            )

        # 5. Provenance Extraction & Comparison
        prov_a = cls._extract_provenance(eval_a)
        prov_b = cls._extract_provenance(eval_b)

        prov_comp: Dict[str, Any] = {
            "provider_transition": f"{prov_a.provider or 'unknown'} -> {prov_b.provider or 'unknown'}",
            "model_transition": f"{prov_a.model or 'unknown'} -> {prov_b.model or 'unknown'}",
            "duration_ms_delta": (prov_b.duration_ms - prov_a.duration_ms) if prov_a.duration_ms is not None and prov_b.duration_ms is not None else None,
            "token_usage_delta": (prov_b.token_usage - prov_a.token_usage) if prov_a.token_usage is not None and prov_b.token_usage is not None else None,
            "estimated_cost_delta": round(prov_b.estimated_cost - prov_a.estimated_cost, 4) if prov_a.estimated_cost is not None and prov_b.estimated_cost is not None else None,
        }

        # 6. Deterministic Executive Summary
        improved_cnt = sum(1 for d in dimensions_list if d.status == "improved")
        declined_cnt = sum(1 for d in dimensions_list if d.status == "declined")
        unchanged_cnt = sum(1 for d in dimensions_list if d.status == "unchanged")
        unavailable_cnt = sum(1 for d in dimensions_list if d.status == "unavailable")

        score_desc = f"{overall_score.formatted_delta} points" if overall_score.formatted_delta else "N/A"
        summary_text = (
            f"Overall score changed by {score_desc} "
            f"({overall_score.value_a if overall_score.value_a is not None else 'N/A'} -> "
            f"{overall_score.value_b if overall_score.value_b is not None else 'N/A'}, "
            f"{overall_score.status.capitalize()}). "
            f"Dimensions: {improved_cnt} improved, {declined_cnt} declined, {unchanged_cnt} unchanged"
        )
        if unavailable_cnt > 0:
            summary_text += f", {unavailable_cnt} unavailable."
        else:
            summary_text += "."

        return EvaluationVersionComparisonResponse(
            idea_id=str(eval_a.idea_id),
            evaluation_a=prov_a,
            evaluation_b=prov_b,
            overall_score=overall_score,
            confidence=confidence_delta,
            dimensions=dimensions_list,
            swot=swot_map,
            sections=sections,
            provenance_comparison=prov_comp,
            summary=summary_text,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )


evaluation_version_comparison_service = EvaluationVersionComparisonService()
