from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.evaluation import Evaluation

class ComparisonService:
    @staticmethod
    async def compare_evaluations(db: AsyncSession, evaluation_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Retrieves multiple evaluations and structures comparison matrices.
        """
        if not evaluation_ids:
            return []

        result = await db.execute(select(Evaluation).where(Evaluation.id.in_(evaluation_ids)))
        evaluations = result.scalars().all()
        
        comparison_matrix = []
        for ev in evaluations:
            payload = ev.result_payload or {}
            dims = payload.get("dimensions", {})
            meta = payload.get("metadata", {})
            
            comparison_matrix.append({
                "evaluation_id": ev.id,
                "idea_id": ev.idea_id,
                "overall_score": payload.get("score", 70),
                "summary": payload.get("summary", ""),
                "provider": meta.get("provider", "N/A"),
                "model": meta.get("model", "N/A"),
                "prompt_version": meta.get("prompt_version", "1.0"),
                "created_at": ev.created_at.isoformat() if ev.created_at else None,
                "dimensions": {
                    "innovation": dims.get("innovation", 70),
                    "market": dims.get("market_potential", 70),
                    "execution": dims.get("execution_complexity", 70),
                    "technical": dims.get("technical_feasibility", 70),
                    "business": dims.get("business_viability", 70),
                    "scalability": dims.get("scalability", 70),
                    "investment": dims.get("competitive_differentiation", 70)
                }
            })
            
        return comparison_matrix

comparison_service = ComparisonService()
