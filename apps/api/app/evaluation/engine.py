import time
import math
from typing import Dict, Any, List, Optional
from app.models.idea import Idea

class DeterministicEvaluationEngine:
    """
    Sprint 2.5 & 2.6 Deterministic Evaluation Engine.
    
    100% Deterministic, offline, rule-based evaluation pipeline.
    Zero external AI, zero LLMs, zero network calls, zero external dependencies.
    """
    
    @classmethod
    def evaluate(cls, idea: Idea) -> Dict[str, Any]:
        """
        Executes deterministic evaluation across 5 stages:
        1. Validation
        2. Rule Execution
        3. Dimension Scoring
        4. Insight & SWOT Generation
        5. Payload Assembly
        """
        start_time = time.time()
        
        # 1. Validation Stage
        cls._validate_idea(idea)
        
        # Extract fields
        title = (idea.title or "").strip()
        problem = (idea.problem_statement or "").strip()
        solution = (idea.solution_description or "").strip()
        target_users = (idea.target_users or "").strip()
        industry = (idea.industry or "").strip()
        business_model = (idea.business_model or "").strip()
        stage = (idea.stage or "").strip()
        tags = (idea.tags or "").strip()
        notes = (idea.notes or "").strip()
        
        # 2. Rule Execution Stage
        problem_len = len(problem.split())
        solution_len = len(solution.split())
        total_len = problem_len + solution_len
        
        # Check completeness keywords
        b2b_keywords = {"enterprise", "b2b", "saas", "api", "platform", "workflow", "compliance", "automation", "dashboard"}
        has_b2b = any(kw in (problem + " " + solution + " " + industry + " " + business_model).lower() for kw in b2b_keywords)
        
        tech_keywords = {"ai", "ml", "cloud", "database", "python", "fastapi", "react", "next.js", "docker", "postgres", "distributed", "kubernetes", "microservices"}
        tech_count = sum(1 for kw in tech_keywords if kw in (problem + " " + solution + " " + notes).lower())
        
        has_target = len(target_users) >= 5
        has_industry = len(industry) >= 3
        has_biz_model = len(business_model) >= 5
        
        # 3. Dimension Scoring Stage
        # Base scores calculated deterministically from text depth and structure
        base = min(60 + (total_len // 5), 85)
        
        innovation_score = min(70 + (tech_count * 4) + (5 if "unique" in solution.lower() or "novel" in solution.lower() else 0), 95)
        market_score = min(65 + (10 if has_b2b else 0) + (10 if has_target else 0) + (5 if has_industry else 0), 92)
        tech_feasibility_score = max(90 - (tech_count * 3) - (5 if total_len < 20 else 0), 55)
        biz_viability_score = min(60 + (15 if has_biz_model else 0) + (10 if has_b2b else 0), 90)
        scalability_score = min(65 + (10 if "saas" in (business_model + industry).lower() or "cloud" in solution.lower() else 0) + (10 if has_b2b else 0), 95)
        exec_complexity_score = min(50 + (tech_count * 5) + (10 if total_len > 100 else 0), 90)
        competitive_diff_score = min(65 + (10 if len(tags) > 3 else 0) + (10 if tech_count >= 2 else 0), 92)
        
        # Overall weighted composite score
        overall_score = round(
            (innovation_score * 0.20) +
            (market_score * 0.20) +
            (tech_feasibility_score * 0.15) +
            (biz_viability_score * 0.15) +
            (scalability_score * 0.15) +
            (competitive_diff_score * 0.15)
        )
        
        # 4. Insights & SWOT Stage
        strengths: List[str] = []
        weaknesses: List[str] = []
        recommendations: List[str] = []
        
        if total_len > 40:
            strengths.append("Comprehensive problem statement and solution definition provided.")
        else:
            weaknesses.append("Problem and solution descriptions are brief; consider providing more operational context.")
            
        if has_b2b:
            strengths.append("Targeting high-margin B2B/Enterprise SaaS monetization channel.")
        else:
            recommendations.append("Define explicit B2B enterprise tier or SaaS recurring revenue model.")
            
        if has_target:
            strengths.append(f"Clear target user persona defined: {target_users}.")
        else:
            weaknesses.append("Target user segment is currently vague or undefined.")
            recommendations.append("Specify exact customer demographic and ideal customer profile (ICP).")
            
        if tech_count >= 2:
            strengths.append("Strong technological architecture alignment with modern cloud stack.")
        else:
            recommendations.append("Specify technical stack components and API integration requirements.")
            
        if not has_biz_model:
            weaknesses.append("Business monetization model needs further definition.")
            recommendations.append("Outline primary revenue streams (e.g., subscription, usage-based pricing).")
            
        if not strengths:
            strengths.append("Foundational startup idea concept with initial structure.")
            
        if not weaknesses:
            weaknesses.append("Competition with existing market incumbents and low switching costs.")
            
        if not recommendations:
            recommendations.append("Conduct customer discovery interviews to validate problem severity.")
            
        summary = (
            f"Evaluation for '{title}': Overall score of {overall_score}/100. "
            f"Concept exhibits strong potential in {industry or 'the target market'} with "
            f"{'high' if innovation_score >= 85 else 'solid'} technical feasibility."
        )
        
        architecture_breakdown = (
            f"### Deterministic Technical Architecture Blueprint\n\n"
            f"- **Core Stack**: FastAPI backend, Async PostgreSQL, React/Next.js frontend\n"
            f"- **Execution Engine**: In-process deterministic evaluator with state machine lifecycle\n"
            f"- **Data Isolation**: Multi-tenant database scoping enforcing strict user ownership\n"
            f"- **Target Stage**: {stage or 'Early Prototype'}"
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 5. Result Payload Assembly
        return {
            "score": overall_score,
            "confidence": 0.95,
            "dimensions": {
                "innovation": innovation_score,
                "market_potential": market_score,
                "technical_feasibility": tech_feasibility_score,
                "business_viability": biz_viability_score,
                "scalability": scalability_score,
                "execution_complexity": exec_complexity_score,
                "competitive_differentiation": competitive_diff_score,
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "summary": summary,
            "architecture_breakdown": architecture_breakdown,
            "metadata": {
                "provider": "deterministic-engine-v2.6",
                "model": "rule-based-v2.6",
                "prompt_version": "2.6-deterministic",
                "temperature": 0.0,
                "max_tokens": 0,
                "duration_ms": duration_ms,
                "token_usage": 0,
                "estimated_cost": 0.0,
                "cached": False,
            }
        }
        
    @staticmethod
    def _validate_idea(idea: Idea) -> None:
        if not idea:
            raise ValueError("Idea record cannot be None.")
        if not idea.title or not idea.title.strip():
            raise ValueError("Idea title is required for deterministic evaluation.")
        if not idea.problem_statement or not idea.problem_statement.strip():
            raise ValueError("Problem statement is required for deterministic evaluation.")
        if not idea.solution_description or not idea.solution_description.strip():
            raise ValueError("Solution description is required for deterministic evaluation.")
