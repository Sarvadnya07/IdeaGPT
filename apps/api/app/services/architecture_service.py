from typing import Dict, Any, List, Optional
import json
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.models.project import Project
from app.models.idea import Idea
from app.models.evaluation import Evaluation

logger = logging.getLogger(__name__)

class ArchitectureService:
    @staticmethod
    def generate_tech_stack(
        category: str = "B2B SaaS",
        title: str = "Startup Concept",
        requirements_focus: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Generates deterministic, production-ready technology stack recommendations
        tailored to project category, idea domain, and architectural requirements.
        """
        cat_lower = category.lower()

        # Tailored selections based on category
        if "fintech" in cat_lower or "security" in cat_lower:
            backend_lang = "Python / Rust"
            backend_fw = "FastAPI + asyncpg"
            db_choice = "PostgreSQL (ACID-compliant with Row-Level Security)"
            cache_choice = "Redis (Cluster + Durable Replication)"
            auth_choice = "Clerk Enterprise + WebAuthn / MFA"
            devops_choice = "AWS ECS Fargate / Terraform with SOC2 Audit Logging"
        elif "ecommerce" in cat_lower or "b2c" in cat_lower:
            backend_lang = "TypeScript / Node.js"
            backend_fw = "Next.js App Router + tRPC / FastAPI"
            db_choice = "PostgreSQL + Stripe Webhook Event Store"
            cache_choice = "Upstash Redis / Cloudflare KV"
            auth_choice = "Clerk Auth / NextAuth"
            devops_choice = "Vercel + AWS Aurora Serverless"
        elif "health" in cat_lower:
            backend_lang = "Python 3.12+"
            backend_fw = "FastAPI with HIPAA-compliant encrypted data layers"
            db_choice = "PostgreSQL (Encrypted at Rest with AES-256)"
            cache_choice = "Redis TLS"
            auth_choice = "Clerk with HIPAA BAA compliance"
            devops_choice = "AWS GovCloud / Dedicated ECS VPC"
        else: # Standard B2B SaaS / General
            backend_lang = "Python 3.12+ & TypeScript"
            backend_fw = "FastAPI & Next.js App Router"
            db_choice = "PostgreSQL (SQLAlchemy Async + Alembic)"
            cache_choice = "Redis / In-memory LRU Cache"
            auth_choice = "Clerk JWT (RS256 JWKS validation)"
            devops_choice = "Docker, Turborepo, GitHub Actions, AWS/Vercel"

        return {
            "title": title,
            "category": category,
            "focus": requirements_focus,
            "frontend": {
                "framework": "Next.js 15+ (React 19, App Router, RSC)",
                "styling": "TailwindCSS v4 & Lucide Icons",
                "state_management": "TanStack React Query v5 & Zustand",
                "component_library": "Radix UI / Headless UI with Framer Motion",
                "build_tooling": "Turbopack & Turborepo"
            },
            "backend": {
                "language": backend_lang,
                "framework": backend_fw,
                "api_protocol": "RESTful OpenAPI 3.1 & Async Server-Sent Events (SSE)",
                "validation": "Pydantic v2 with strict schemas",
                "rate_limiting": "SlowAPI (Token Bucket / Sliding Window)"
            },
            "database_and_caching": {
                "primary_database": db_choice,
                "caching_layer": cache_choice,
                "migrations": "Alembic with Zero Schema-Drift CI verification",
                "orm": "SQLAlchemy 2.0 Asyncio",
                "vector_database": "pgvector / Pinecone (for AI context embeddings)"
            },
            "ai_and_ml": {
                "inference_providers": "Groq (Llama 3.3 70B / 8B Instant) & OpenAI / Gemini Fallbacks",
                "orchestration": "Custom Provider-Agnostic AIRouter with Dynamic Discovery",
                "caching": "Deterministic SQLite/Redis prompt response cache",
                "output_validation": "Pydantic JSON Repair & Semantic Guardrails"
            },
            "devops_and_security": {
                "hosting": devops_choice,
                "authentication": auth_choice,
                "ci_cd": "GitHub Actions (Pytest, Vitest, Playwright, Turborepo Cache)",
                "observability": "Structured JSON logging with request-id propagation & SlowAPI metrics"
            },
            "architectural_tradeoffs": [
                {
                    "decision": "FastAPI + Next.js Monorepo (Turborepo)",
                    "pros": "Drastically superior Python ecosystem for AI reasoning paired with top-tier React Server Components frontend performance.",
                    "cons": "Requires maintaining two language runtimes (Node.js & Python)."
                },
                {
                    "decision": "PostgreSQL with asyncpg",
                    "pros": "Non-blocking high-concurrency database I/O with ACID guarantees and JSONB flexibility.",
                    "cons": "Requires careful connection pool tuning under heavy concurrent LLM waits."
                },
                {
                    "decision": "Groq LPU Inference with Fallback Router",
                    "pros": "Sub-second inference speed (250-500ms) with extremely low cost per million tokens.",
                    "cons": "Requires graceful fallback to OpenAI/Gemini if project limits or specific models are restricted."
                }
            ]
        }

    @staticmethod
    def generate_architecture_blueprint(
        title: str = "Startup System",
        category: str = "B2B SaaS",
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Generates system topology, database ER schema, API specs, and security blueprints.
        """
        return {
            "title": title,
            "category": category,
            "description": description or "Cloud-native scalable AI co-founder architecture.",
            "topology": {
                "client_layer": "Next.js Web Client (Vercel Edge CDN)",
                "api_gateway": "FastAPI API Service (AWS ECS / Docker / Port 8000)",
                "database_layer": "PostgreSQL Database (Multi-AZ with asyncpg connection pooling)",
                "ai_inference_layer": "Groq LPU Cluster (OpenAI-compatible /chat/completions)",
                "cache_and_queue": "Redis / In-memory Task Queue with Idempotency",
                "auth_provider": "Clerk (RS256 JWKS Verification)"
            },
            "mermaid_diagram": """graph TD
    Client[Web Browser / Next.js] -->|HTTPS REST| APIGateway[FastAPI Application]
    APIGateway -->|JWT Validation| Clerk[Clerk JWKS Auth]
    APIGateway -->|Async ORM| Postgres[(PostgreSQL Database)]
    APIGateway -->|Async HTTP| Groq[Groq LPU Inference API]
    APIGateway -->|Cache Check| Cache[(Cache / Redis)]
    
    subgraph Monorepo Boundary
        Client
        APIGateway
    end
    
    subgraph Data & Storage
        Postgres
        Cache
    end""",
            "api_endpoints": [
                {"method": "POST", "path": "/api/v1/projects/", "description": "Create isolated project workspace"},
                {"method": "GET", "path": "/api/v1/projects/", "description": "List user projects with pagination and search"},
                {"method": "POST", "path": "/api/v1/ideas/", "description": "Persist startup idea parameters and drafts"},
                {"method": "POST", "path": "/api/v1/ideas/{id}/evaluations", "description": "Trigger deterministic AI evaluation"},
                {"method": "POST", "path": "/api/v1/ai/tasks", "description": "Enqueue async AI task with idempotency key"},
                {"method": "POST", "path": "/api/v1/evaluations/compare", "description": "Side-by-side benchmark for 2-5 ideas"},
                {"method": "GET", "path": "/api/v1/analytics/summary", "description": "Aggregate workspace velocity and score trends"}
            ],
            "database_entities": [
                {
                    "table": "users",
                    "columns": ["id (INT PK)", "clerk_id (VARCHAR UNIQUE)", "email (VARCHAR)", "created_at (TIMESTAMP)"],
                    "description": "User identity and tenant anchor."
                },
                {
                    "table": "projects",
                    "columns": ["id (UUID PK)", "user_id (FK users)", "title (VARCHAR)", "slug (VARCHAR UNIQUE)", "status (VARCHAR)", "visibility (VARCHAR)", "deleted_at (TIMESTAMP)"],
                    "description": "Tenant-isolated project workspace."
                },
                {
                    "table": "ideas",
                    "columns": ["id (UUID PK)", "project_id (FK projects)", "title (VARCHAR)", "problem_statement (TEXT)", "solution_description (TEXT)", "stage (VARCHAR)", "is_draft (BOOLEAN)"],
                    "description": "Startup concept specification and parameter inputs."
                },
                {
                    "table": "evaluations",
                    "columns": ["id (UUID PK)", "project_id (FK)", "idea_id (FK)", "status (VARCHAR)", "result_payload (JSON)", "duration_ms (INT)"],
                    "description": "AI analysis scoring, SWOT matrices, and feasibility breakdown."
                },
                {
                    "table": "ai_tasks",
                    "columns": ["id (UUID PK)", "user_id (FK)", "task_type (VARCHAR)", "provider (VARCHAR)", "model (VARCHAR)", "status (VARCHAR)", "idempotency_key (VARCHAR)", "result_payload (JSONB)"],
                    "description": "Asynchronous AI task state machine and token telemetry."
                },
                {
                    "table": "roadmaps",
                    "columns": ["id (VARCHAR PK)", "project_id (FK projects)", "milestones (JSON)", "status (VARCHAR)"],
                    "description": "Project execution timeline and milestone trackers."
                }
            ],
            "security_specifications": [
                "Strict Tenant Isolation: All SQL queries filter by user_id == current_user.id at the ORM layer.",
                "Zero Secret Leakage: API keys (GROQ_API_KEY, DATABASE_URL) strictly reside server-side.",
                "Rate Limiting: SlowAPI token bucket limiting protects inference endpoints against abuse.",
                "CORS & Security Headers: Explicit allowed origins and method whitelist.",
                "Data Sanitization: Pydantic v2 input validation with strict length constraints."
            ]
        }

    @staticmethod
    def generate_prd(
        title: str = "Startup Concept",
        category: str = "B2B SaaS",
        problem_statement: str = "Founders lack rapid technical feasibility validation.",
        solution_description: str = "Automated AI co-founder that scopes architectures and analyzes risk.",
        target_users: str = "Startup Founders, Product Managers, Software Engineers"
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive Product Requirements Document (PRD).
        """
        return {
            "title": f"PRD: {title}",
            "version": "1.0.0",
            "status": "Draft / Approved for Scoping",
            "category": category,
            "target_users": target_users or "Early-stage founders and technical leaders",
            "executive_summary": f"{title} is an automated {category} solution designed to solve the critical problem: {problem_statement}. By offering {solution_description}, it accelerates time-to-market and eliminates technical uncertainty.",
            "problem_definition": {
                "core_problem": problem_statement,
                "current_alternatives": ["Manual agency consulting", "Ad-hoc ChatGPT prompt engineering", "Spreadsheet tracking"],
                "why_now": "Rapid commoditization of LLMs and high cost of engineering rework creates huge demand for automated technical co-founders."
            },
            "user_personas": [
                {
                    "persona": "Solo Technical Founder",
                    "need": "Needs immediate architecture blueprints, database schema outlines, and stack validation before writing code."
                },
                {
                    "persona": "Non-Technical Product Lead",
                    "need": "Needs objective feasibility scoring, risk analysis, and estimated development timelines to present to investors."
                }
            ],
            "functional_requirements": [
                {"id": "FR-1", "feature": "Project Workspace Management", "priority": "P0", "description": "Users must be able to create, search, filter, and archive project workspaces."},
                {"id": "FR-2", "feature": "Idea Parameter Capture", "priority": "P0", "description": "Form inputs for problem statement, solution description, target users, and industry."},
                {"id": "FR-3", "feature": "AI Evaluation Engine", "priority": "P0", "description": "Multidimensional analysis generating overall score (0-100), SWOT, and technical feasibility."},
                {"id": "FR-4", "feature": "Idea Benchmarking", "priority": "P1", "description": "Side-by-side comparative matrix of 2 to 5 ideas with delta rankings."},
                {"id": "FR-5", "feature": "Milestone Roadmap Tracker", "priority": "P1", "description": "Interactive phased milestones with toggleable task states."}
            ],
            "non_functional_requirements": [
                {"id": "NFR-1", "category": "Performance", "target": "API responses under 200ms for CRUD; AI streaming/inference under 2.5s."},
                {"id": "NFR-2", "category": "Security", "target": "Tenant isolation at ORM level, RS256 JWT auth, zero secret leakage."},
                {"id": "NFR-3", "category": "Reliability", "target": "99.9% uptime with idempotent AI task queues and transactional rollbacks."}
            ],
            "success_metrics": [
                {"metric": "Time to Scoped Architecture", "target": "< 60 seconds"},
                {"metric": "Idea Evaluation Completion Rate", "target": "> 85%"},
                {"metric": "User Retention / Project Duplication", "target": "> 40% month-over-month"}
            ]
        }

    @staticmethod
    def generate_pitch_deck_outline(
        title: str = "Startup Concept",
        category: str = "B2B SaaS",
        problem: str = "",
        solution: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Generates a 10-slide venture pitch deck outline.
        """
        prob_text = problem or "Founders spend months and thousands of dollars building the wrong technical architecture."
        sol_text = solution or "An intelligent AI co-founder that validates ideas, designs blueprints, and scopes roadmaps in seconds."

        return [
            {
                "slide_number": 1,
                "title": "Title & Vision",
                "headline": f"{title} — The Intelligent {category} Platform",
                "bullet_points": ["Validating concepts instantly", "The automated technical co-founder for modern startups"]
            },
            {
                "slide_number": 2,
                "title": "The Problem",
                "headline": "Startups Fail From Premature Engineering & Blind Execution",
                "bullet_points": [prob_text, "Lack of instant architectural validation", "High burn rate on unverified features"]
            },
            {
                "slide_number": 3,
                "title": "The Solution",
                "headline": "Instant AI Feasibility, Benchmarks, and Execution Blueprints",
                "bullet_points": [sol_text, "Deterministic multi-dimensional scoring", "Automated roadmapping and stack selection"]
            },
            {
                "slide_number": 4,
                "title": "Market Opportunity (TAM / SAM / SOM)",
                "headline": "$12B+ Global Software Scoping & Co-founder Market",
                "bullet_points": ["TAM: $12B+ Global developer tools & startup SaaS", "SAM: $1.1B Serviceable SaaS market", "SOM: $85M 3-year serviceable obtainable market"]
            },
            {
                "slide_number": 5,
                "title": "Product & Technology",
                "headline": "High-Speed LPU Inference & Enterprise Isolation",
                "bullet_points": ["Sub-second Groq LPU inference", "PostgreSQL tenant-isolated data persistence", "Multi-model fallback & JSON repair engine"]
            },
            {
                "slide_number": 6,
                "title": "Business Model",
                "headline": "High-Margin Tiered SaaS & Usage-Based Pro Plans",
                "bullet_points": ["Freemium tier (3 evaluations/month)", "Pro Tier ($49/month unlimited scoping)", "Enterprise Team ($199/month multi-seat)"]
            },
            {
                "slide_number": 7,
                "title": "Competition & Moat",
                "headline": "Deterministic AI Architecture vs Generic LLM Chat",
                "bullet_points": ["Integrated workspace lifecycle vs disconnected chat", "Side-by-side idea benchmarking engine", "PostgreSQL persistence with zero data leakage"]
            },
            {
                "slide_number": 8,
                "title": "Go-To-Market Strategy",
                "headline": "Developer-Led Growth & Startup Accelerator Partnerships",
                "bullet_points": ["Product-led onboarding with instant demo", "Incubator & accelerator licensing (Y Combinator, Techstars)", "Open-source developer tooling distribution"]
            },
            {
                "slide_number": 9,
                "title": "Financial Projections",
                "headline": "Path to $5M ARR Within 36 Months",
                "bullet_points": ["Year 1: $350k ARR (500 paid teams)", "Year 2: $1.8M ARR (2,500 paid teams)", "Year 3: $5.2M ARR (7,000 paid teams + Enterprise)"]
            },
            {
                "slide_number": 10,
                "title": "The Ask & Team",
                "headline": "Raising $1.5M Seed to Scale Engineering & AI Distribution",
                "bullet_points": ["Use of funds: 60% Engineering & AI infra, 30% GTM & Growth, 10% Operations", "Built by passionate full-stack & AI engineers"]
            }
        ]

architecture_service = ArchitectureService()
