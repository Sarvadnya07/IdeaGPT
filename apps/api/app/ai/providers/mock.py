import json
from typing import Any, Dict
from app.ai.providers.base import AIProvider

class MockProvider(AIProvider):
    async def generate(self, prompt: str, system_prompt: str = "", response_format: str = "json") -> Dict[str, Any]:
        mock_response = {
            "score": 85,
            "strengths": [
                "Strong user demand with high validation need.",
                "SaaS monetization potential.",
                "Robust modern technology recommendations."
            ],
            "weaknesses": [
                "Competition with low-barrier developer wrappers.",
                "Privacy leakage risks from direct client browser integration."
            ],
            "market_analysis": "The automation and AI tooling space is growing aggressively with a dynamic CAGR projection of over 20%.",
            "recommendations": [
                "Introduce localized rate limiting on client-facing API proxies.",
                "Integrate a failover orchestration router."
            ],
            "architecture_breakdown": "### Mock Evaluation Architecture Blueprint\n\n- **Frontend**: Next.js 14+ with local React state\n- **Backend**: FastAPI with async route dependencies\n- **Infrastructure**: Dockerized PostgreSQL database containers."
        }
        if response_format == "json":
            return mock_response
        return {"text": json.dumps(mock_response)}
