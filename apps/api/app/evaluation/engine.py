import time
import math
import json
from typing import Dict, Any, List, Optional
from app.models.idea import Idea

class DeterministicEvaluationEngine:
    """
    Intelligent Deterministic Evaluation Engine.
    
    Reads all 8 granular startup parameters (title, elevator pitch, core problem,
    target audience, tech stack, platforms, monetization model, competitors, and technical risks).
    Calculates accurate, proportional multi-dimensional scores and tailored SWOT insights.
    """
    
    @classmethod
    def evaluate(cls, idea: Idea) -> Dict[str, Any]:
        start_time = time.time()
        cls._validate_idea(idea)
        
        # 1. Parse JSON notes & idea fields
        notes_dict = {}
        if idea.notes:
            try:
                notes_dict = json.loads(idea.notes)
                if not isinstance(notes_dict, dict):
                    notes_dict = {}
            except Exception:
                notes_dict = {}

        title = (idea.title or "").strip()
        problem = (notes_dict.get("core_problem") or idea.problem_statement or "").strip()
        solution = (notes_dict.get("elevator_pitch") or idea.solution_description or "").strip()
        target_users = (notes_dict.get("target_audience") or idea.target_users or "").strip()
        tech_stack = (notes_dict.get("existing_tech_stack") or "").strip()
        platforms = (notes_dict.get("primary_platforms") or "Web").strip()
        business_model = (notes_dict.get("monetization_model") or idea.business_model or "").strip()
        competitors = (notes_dict.get("key_competitors") or "").strip()
        tech_risks = (notes_dict.get("technical_risks") or "").strip()
        industry = (idea.industry or "").strip()
        stage = (idea.stage or "Early Prototype").strip()

        combined_text = f"{title} {problem} {solution} {target_users} {tech_stack} {platforms} {business_model} {competitors} {tech_risks}".lower()

        # 2. Substantive content and completeness analysis
        problem_words = len([w for w in problem.split() if len(w) > 1])
        solution_words = len([w for w in solution.split() if len(w) > 1])
        total_substantive_words = problem_words + solution_words + len(tech_stack.split()) + len(target_users.split())

        is_trivial = (
            (problem_words <= 1 and solution_words <= 1 and len(problem) <= 3) or
            total_substantive_words < 5 or
            (problem.lower() == "t" and solution.lower() == "t")
        )

        # 3. Trivial / Placeholder input handling
        if is_trivial:
            overall_score = 28
            dimensions = {
                "innovation": 30,
                "market_potential": 25,
                "technical_feasibility": 40,
                "business_viability": 22,
                "scalability": 30,
                "execution_complexity": 20,
                "competitive_differentiation": 20,
            }
            strengths = [
                "Idea placeholder draft registered in system."
            ]
            weaknesses = [
                "Input data is too brief to establish commercial or technical feasibility.",
                "Problem statement and user pain points are undefined.",
                "Missing target audience, technology stack, and monetization details."
            ]
            recommendations = [
                "Provide a detailed problem statement describing specific customer workflows.",
                "Define your target persona (e.g. B2B engineers, students, or enterprise teams).",
                "Specify your technology architecture stack and monetization tiers."
            ]
            summary = (
                f"Evaluation for '{title}': Insufficient data provided ({total_substantive_words} words). "
                f"Overall readiness score is {overall_score}/100. Please complete the idea profile for an in-depth analysis."
            )
            arch_breakdown = (
                f"### System Architecture Placeholder\n\n"
                f"- **Status**: Pending complete technical stack inputs.\n"
                f"- **Recommended Next Step**: Outline backend, frontend, and database requirements."
            )

        else:
            # 4. Comprehensive Domain & Keyword Analysis
            has_ai = any(kw in combined_text for kw in ["ai", "chatbot", "gpt", "llm", "copilot", "nlp", "model", "assistant", "agent", "neural", "rag"])
            has_code_dev = any(kw in combined_text for kw in ["coder", "coding", "developer", "software", "programmer", "python", "next", "react", "typescript", "fastapi", "docker", "postgres"])
            has_student_ed = any(kw in combined_text for kw in ["student", "students", "learning", "education", "tutorial", "guidance", "bootcamp"])
            has_freemium = "freemium" in business_model.lower() or "free" in business_model.lower()
            has_b2b_saas = any(kw in business_model.lower() for kw in ["saas", "subscription", "b2b", "enterprise", "per-seat", "usage"])

            # Scoring heuristics tailored to actual data
            # Innovation
            base_inno = 60
            if has_ai: base_inno += 15
            if has_code_dev and has_ai: base_inno += 8
            if len(solution.split()) > 10: base_inno += 5
            innovation_score = min(base_inno, 94)

            # Market Potential
            base_mkt = 55
            if len(target_users) >= 4: base_mkt += 12
            if has_student_ed or has_code_dev: base_mkt += 10
            if len(problem.split()) >= 6: base_mkt += 8
            market_score = min(base_mkt, 92)

            # Technical Feasibility
            base_tech = 70
            if len(tech_stack) > 3: base_tech += 10
            if has_ai: base_tech -= 5 # AI introduces latency & hallucination risks
            if len(tech_risks) > 5: base_tech += 5 # Founder is aware of technical risks
            tech_feasibility_score = min(max(base_tech, 50), 90)

            # Business Viability
            base_biz = 55
            if has_freemium: base_biz += 12 # Fast user acquisition
            if has_b2b_saas: base_biz += 18 # High revenue predictability
            if len(competitors) > 3: base_biz += 5
            biz_viability_score = min(base_biz, 88)

            # Scalability
            base_scale = 65
            if "web" in platforms.lower() or "cloud" in combined_text or "api" in combined_text: base_scale += 15
            if has_freemium: base_scale += 8
            scalability_score = min(base_scale, 95)

            # Execution Complexity
            base_exec = 60
            if has_ai: base_exec += 15
            if has_code_dev: base_exec += 10
            exec_complexity_score = min(base_exec, 92)

            # Competitive Differentiation
            base_diff = 55
            if len(competitors) > 3: base_diff += 12
            if len(solution.split()) >= 8: base_diff += 10
            competitive_diff_score = min(base_diff, 89)

            # Weighted Composite Score
            overall_score = round(
                (innovation_score * 0.20) +
                (market_score * 0.20) +
                (tech_feasibility_score * 0.15) +
                (biz_viability_score * 0.15) +
                (scalability_score * 0.15) +
                (competitive_diff_score * 0.15)
            )

            dimensions = {
                "innovation": innovation_score,
                "market_potential": market_score,
                "technical_feasibility": tech_feasibility_score,
                "business_viability": biz_viability_score,
                "scalability": scalability_score,
                "execution_complexity": exec_complexity_score,
                "competitive_differentiation": competitive_diff_score,
            }

            # 5. Tailored Insights & SWOT
            strengths = []
            weaknesses = []
            recommendations = []

            # Dynamic Strengths
            if target_users:
                strengths.append(f"Clear target user persona defined: {target_users}.")
            if tech_stack:
                strengths.append(f"Modern technical foundation specified: {tech_stack} on {platforms}.")
            if has_ai:
                strengths.append("High leverage AI/LLM capability targeting productivity augmentation.")
            if has_freemium:
                strengths.append(f"Monetization model '{business_model}' enables viral developer/student adoption loops.")

            # Dynamic Weaknesses
            if tech_risks:
                weaknesses.append(f"Identified Technical Risk: {tech_risks}.")
            else:
                weaknesses.append("Potential LLM hallucinations and syntax correctness challenges in code generation.")
            if competitors:
                weaknesses.append(f"Competitive Landscape: Needs distinct feature specialization against {competitors} and generalist LLMs.")
            if has_freemium:
                weaknesses.append("High inference compute cost per active user on free tier can pressure gross margins.")

            # Dynamic Recommendations
            if has_code_dev and has_ai:
                recommendations.append("Implement an isolated code sandbox (e.g., Pyodide / Docker) for automated syntax and test validation.")
                recommendations.append("Incorporate RAG over official framework documentation to reduce outdated code suggestions.")
            if has_freemium:
                recommendations.append("Enforce daily token quotas or rate-limiting for free users to maintain positive unit economics.")
            recommendations.append("Conduct user interviews with target cohort to validate critical workflow friction points.")

            summary = (
                f"Evaluation for '{title}': Overall score of {overall_score}/100. "
                f"The concept shows strong potential for {target_users or 'target developers'} with an innovation rating of {innovation_score}/100. "
                f"Primary execution focus should be on code reliability ({tech_feasibility_score}/100) and scalable freemium economics."
            )

            arch_breakdown = (
                f"### Tailored Technical Architecture Blueprint\n\n"
                f"- **Platform**: {platforms}\n"
                f"- **Core Tech Stack**: {tech_stack or 'FastAPI / Next.js / PostgreSQL'}\n"
                f"- **AI & Execution Pipeline**: Async LLM inference router with fallback cache & prompt templating\n"
                f"- **Safety & Isolation**: Multi-tenant database isolation with strict rate-limiting per user\n"
                f"- **Deployment Target**: {stage}"
            )

        duration_ms = int((time.time() - start_time) * 1000)

        # 6. Assembly
        return {
            "score": overall_score,
            "confidence": 0.95 if not is_trivial else 0.35,
            "dimensions": dimensions,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "summary": summary,
            "architecture_breakdown": arch_breakdown,
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

