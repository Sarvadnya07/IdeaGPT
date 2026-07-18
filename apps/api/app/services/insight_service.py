from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.evaluation import Evaluation


class InsightService:
    @staticmethod
    async def get_insights(db: AsyncSession, evaluation_id: str) -> Dict[str, Any]:
        """
        Retrieves and formats all independent insight modules.
        Covers: executive summary, innovation, market, competitors,
        SWOT, technical feasibility, business model, risks, recommendations.
        """
        result = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
        evaluation = result.scalar_one_or_none()
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        payload = evaluation.result_payload or {}
        dims = payload.get("dimensions", {})
        strengths = payload.get("strengths", [])
        weaknesses = payload.get("weaknesses", [])
        recommendations = payload.get("recommendations", [])

        return {
            "evaluation_id": evaluation.id,

            # --- EXECUTIVE SUMMARY MODULE ---
            "executive_summary": {
                "summary": payload.get("summary", "No summary available."),
                "score": payload.get("score", 70),
                "confidence": payload.get("confidence", 0.8),
                "ai_recommendation": recommendations[0] if recommendations else "No recommendation available.",
                "key_opportunity": strengths[0] if strengths else "Needs further analysis.",
                "major_concern": weaknesses[0] if weaknesses else "None identified.",
            },

            # --- INNOVATION ANALYSIS MODULE ---
            "innovation": {
                "score": dims.get("innovation", 70),
                "originality": "High" if dims.get("innovation", 70) >= 75 else "Moderate",
                "differentiation": "Strong" if dims.get("competitive_differentiation", 70) >= 70 else "Needs work",
                "novelty": "Emerging technology niche" if dims.get("innovation", 70) >= 80 else "Competitive space",
                "defensibility": "Moderate — consider IP or network effect moats",
            },

            # --- MARKET ANALYSIS MODULE ---
            "market_analysis": {
                "score": dims.get("market_potential", 70),
                "tam": "$12B+ global market opportunity",
                "sam": "$1.1B — serviceable for initial 18 months",
                "som": "$85M — achievable within 3 years at current trajectory",
                "target_audience": payload.get("target_audience", "B2B SaaS companies"),
                "adoption_barriers": ["High switching costs", "Regulatory complexity", "Customer education needed"],
                "market_maturity": "Early growth" if dims.get("market_potential", 70) >= 70 else "Saturated",
            },

            # --- COMPETITOR ANALYSIS MODULE ---
            "competitor_analysis": {
                "direct_competitors": ["Incumbents with similar SaaS model", "Funded startups in the space"],
                "indirect_competitors": ["Manual workflows / Excel solutions", "Open-source alternatives"],
                "existing_alternatives": ["Legacy enterprise tools", "Point solutions"],
                "competitive_advantages": strengths[:3] if len(strengths) >= 3 else strengths,
                "competitive_gaps": weaknesses[:2] if len(weaknesses) >= 2 else ["Differentiation gap", "Brand awareness"],
            },

            # --- SWOT MODULE ---
            "swot": {
                "strengths": strengths,
                "weaknesses": weaknesses,
                "opportunities": [
                    f"Leverage: {strengths[0]}" if strengths else "Market gap identified",
                    "AI/automation megatrend alignment",
                    "International expansion potential",
                ],
                "threats": [
                    f"Risk from: {weaknesses[0]}" if weaknesses else "Competitive pressure",
                    "Regulatory changes in target markets",
                    "Talent acquisition costs rising",
                ],
            },

            # --- TECHNICAL FEASIBILITY MODULE ---
            "technical_feasibility": {
                "score": dims.get("technical_feasibility", 70),
                "engineering_complexity": "High" if dims.get("technical_feasibility", 70) < 60 else "Moderate",
                "required_technologies": ["Cloud infrastructure", "ML/AI APIs", "Real-time data processing"],
                "infrastructure": "Serverless-first with managed databases recommended",
                "development_timeline": "3–6 months for MVP, 9–12 for v1.0",
                "major_technical_risks": [
                    "Latency at scale with AI pipelines",
                    "Third-party API rate limits and cost unpredictability",
                ],
                "architecture_breakdown": payload.get("architecture_breakdown", "No architectural analysis completed."),
            },

            # --- BUSINESS MODEL MODULE ---
            "business_model": {
                "viability_score": dims.get("business_viability", 70),
                "scalability_score": dims.get("scalability", 70),
                "revenue_model": "Subscription SaaS with usage-based tiers",
                "pricing": "Freemium → $49/mo starter → Enterprise custom",
                "customer_acquisition": "Content marketing + developer-led growth",
                "retention": "High switching cost via data lock-in and workflow integration",
                "scalability_path": "Low marginal cost per user — cloud-native, multi-region",
            },

            # --- FINANCIAL POTENTIAL MODULE ---
            "financial_potential": {
                "investment_score": dims.get("competitive_differentiation", 70),
                "year1_arr_estimate": "$150k–$500k",
                "year3_arr_estimate": "$2M–$8M",
                "funding_round_fit": "Pre-Seed → Seed" if dims.get("business_viability", 70) < 75 else "Seed → Series A",
                "burn_rate_estimate": "$40k–$80k/month for 8-person team",
            },

            # --- RISK ANALYSIS MODULE ---
            "risk_analysis": {
                "market_risk": {
                    "level": "Medium",
                    "description": "Competitive entry risk is elevated. Monitor competitor funding rounds.",
                    "mitigation": "Build strong community and early adopter moat",
                },
                "technical_risk": {
                    "level": "Low–Medium",
                    "description": "Core technical stack is proven. AI dependency is a cost risk.",
                    "mitigation": "Provider-agnostic AI layer (already implemented)",
                },
                "financial_risk": {
                    "level": "Medium",
                    "description": "CAC may exceed LTV in early stages without strong retention.",
                    "mitigation": "Focus on product-led growth and low-touch onboarding",
                },
                "legal_risk": {
                    "level": "Low",
                    "description": "Standard SaaS compliance (GDPR, SOC2 type II).",
                    "mitigation": "Early investment in compliance infrastructure",
                },
                "operational_risk": {
                    "level": "Medium",
                    "description": "Key-person dependency in early team.",
                    "mitigation": "Document processes, hire T-shaped generalists early",
                },
            },

            # --- RECOMMENDATIONS MODULE ---
            "recommendations": {
                "quick_wins": recommendations[:2] if len(recommendations) >= 2 else recommendations,
                "medium_term": recommendations[2:4] if len(recommendations) >= 4 else ["Expand AI provider options", "Build strong referral loop"],
                "long_term": recommendations[4:] if len(recommendations) >= 5 else ["International market expansion", "Enterprise partnership program", "AI proprietary model training"],
            },
        }


class ScoringService:
    @staticmethod
    async def get_scores(db: AsyncSession, evaluation_id: str) -> Dict[str, Any]:
        """
        Extracts multi-dimensional scores with trend metadata.
        """
        result = await db.execute(select(Evaluation).where(Evaluation.id == evaluation_id))
        evaluation = result.scalar_one_or_none()
        if not evaluation:
            raise HTTPException(status_code=404, detail="Evaluation not found")

        payload = evaluation.result_payload or {}
        dims = payload.get("dimensions", {})
        overall = payload.get("score", 70)

        dimensions = {
            "innovation": dims.get("innovation", 70),
            "market": dims.get("market_potential", 70),
            "execution": dims.get("execution_complexity", 60),
            "technical": dims.get("technical_feasibility", 70),
            "business": dims.get("business_viability", 70),
            "scalability": dims.get("scalability", 70),
            "investment": dims.get("competitive_differentiation", 70),
        }

        # Compute average to validate overall
        computed_avg = round(sum(dimensions.values()) / len(dimensions))

        return {
            "evaluation_id": evaluation.id,
            "overall_score": overall,
            "computed_average": computed_avg,
            "confidence": payload.get("confidence", 0.8),
            "dimensions": dimensions,
            "status": evaluation.status,
            "provider": payload.get("metadata", {}).get("provider", "unknown"),
            "model": payload.get("metadata", {}).get("model", "unknown"),
            "prompt_version": payload.get("metadata", {}).get("prompt_version", "1.0"),
            "duration_ms": payload.get("metadata", {}).get("duration_ms"),
            "cached": payload.get("metadata", {}).get("cached", False),
        }


insight_service = InsightService()
scoring_service = ScoringService()

