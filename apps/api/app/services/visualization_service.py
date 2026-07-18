from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.evaluation import Evaluation


class VisualizationService:
    """Prepares normalized, chart-ready data for frontend visualizations."""

    @staticmethod
    async def get_chart_data(db: AsyncSession, evaluation_id: str) -> Dict[str, Any]:
        result = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
        evaluation = result.scalar_one_or_none()
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        payload = evaluation.result_payload or {}
        dims = payload.get("dimensions", {})

        # Radar chart axes: normalized 0–100
        radar = [
            {"axis": "Innovation", "value": dims.get("innovation", 70)},
            {"axis": "Market", "value": dims.get("market_potential", 70)},
            {"axis": "Execution", "value": dims.get("execution_complexity", 60)},
            {"axis": "Technical", "value": dims.get("technical_feasibility", 70)},
            {"axis": "Business", "value": dims.get("business_viability", 70)},
            {"axis": "Scalability", "value": dims.get("scalability", 70)},
            {"axis": "Investment", "value": dims.get("competitive_differentiation", 70)},
        ]

        # Bar chart for horizontal comparison
        bar = [
            {"category": "Strengths", "count": len(payload.get("strengths", []))},
            {"category": "Weaknesses", "count": len(payload.get("weaknesses", []))},
            {"category": "Recommendations", "count": len(payload.get("recommendations", []))},
        ]

        # Risk heatmap: 1–4 severity
        risk_matrix = [
            {"category": "Market Risk", "likelihood": 3, "impact": 3},
            {"category": "Technical Risk", "likelihood": 2, "impact": 4},
            {"category": "Financial Risk", "likelihood": 2, "impact": 3},
            {"category": "Legal Risk", "likelihood": 1, "impact": 2},
            {"category": "Operational Risk", "likelihood": 3, "impact": 2},
        ]

        return {
            "evaluation_id": evaluation_id,
            "overall_score": payload.get("score", 70),
            "radar": radar,
            "bar": bar,
            "risk_matrix": risk_matrix,
            "confidence": payload.get("confidence", 0.8),
            "dimensions": {
                "innovation": dims.get("innovation", 70),
                "market": dims.get("market_potential", 70),
                "execution": dims.get("execution_complexity", 60),
                "technical": dims.get("technical_feasibility", 70),
                "business": dims.get("business_viability", 70),
                "scalability": dims.get("scalability", 70),
                "investment": dims.get("competitive_differentiation", 70),
            }
        }


visualization_service = VisualizationService()
