# System Architecture & Technical Design

IdeaGPT employs a decoupled client-server architecture managed within a Turborepo monorepo. This approach optimizes for separation of concerns while maintaining excellent Developer Experience (DX), unified continuous integration, and shared tooling.

---

## 🏗 1. High-Level System Topology

```mermaid
graph TD
    Client[Web Browser / Mobile Client] -->|HTTPS / Next.js Routing| WebApp[Next.js 16 App Router / apps/web]
    Client -->|OAuth / Session Minting| ClerkAuth[Clerk Identity Provider]
    WebApp -->|HTTPS / REST API + SSE| BackendAPI[FastAPI Gateway / apps/api]
    BackendAPI -->|Cryptographic RS256 JWKS Verification| ClerkAuth
    BackendAPI -->|Async Connection Pool| Database[(PostgreSQL 15+ Database)]
    BackendAPI -->|Rate Limit Storage| RedisStore[(Redis 7)]
    BackendAPI -->|Dynamic LLM Routing| GroqLPU[Groq LPU / Llama 3.3 70B]
    BackendAPI -->|Fallback LLM Routing| OpenAIAPI[OpenAI / Gemini / Ollama]

    subgraph Turborepo Monorepo Boundary
        WebApp
        BackendAPI
        SharedUI[packages/ui]
        SharedConfig[packages/typescript-config]
    end

    SharedUI -.-> WebApp
    SharedConfig -.-> WebApp
```

---

## 🧩 2. Layered Architecture & Module Boundaries

The backend application (`apps/api/app`) follows a strict layered architecture to ensure high cohesion and low coupling:

```
apps/api/app/
├── core/           # Low-level primitives: Config, Security (ClerkAuth), Logging, Rate-Limiting, DB Engine
├── db/             # Session lifecycle, Base declarative metadata, Migrations
├── models/         # SQLAlchemy 2.0 Entities with explicit Foreign Keys & Cascades
├── schemas/        # Pydantic v2 DTOs with strict input validation & output serialization
├── api/            # HTTP Presentation: Dependencies (Auth, Roles), Routers, Middleware
├── services/       # Domain business logic: Analytics, Comparison, Architecture, Quotas, Registry
├── evaluation/     # Core Engine: Coordinator (FSM), Executor (Tx Boundaries), Deterministic Engine
├── ai/             # AI Subsystem: Orchestrator, Dynamic Router, Provider Adapters, Guardrails
└── workers/        # Asynchronous task worker integration (FastAPI BackgroundTasks & Celery)
```

---

## 🔄 3. Evaluation Execution Lifecycle & State Machine

Evaluations follow a strictly enforced Finite State Machine (FSM) with isolated database transactions:

```mermaid
stateDiagram-v2
    [*] --> PENDING: POST /api/v1/ideas/{id}/evaluations (Tx 1)
    PENDING --> RUNNING: EvaluationExecutor.execute() (Tx 2)
    RUNNING --> COMPLETED: DeterministicEngine Success (Tx 3)
    RUNNING --> FAILED: Engine Exception / Stale Recovery
    PENDING --> CANCELLED: User Cancellation
    RUNNING --> CANCELLED: User Cancellation
    FAILED --> PENDING: POST /evaluations/{id}/retry
    CANCELLED --> PENDING: POST /evaluations/{id}/retry
    COMPLETED --> [*]
    FAILED --> [*]
    CANCELLED --> [*]
```

---

## ⚡ 4. Real-Time Streaming & AI Task Pipeline

In addition to fast synchronous deterministic evaluations ($<50$ms), long-running AI generation jobs utilize Server-Sent Events (SSE) streaming:

1. **Task Dispatch**: Client submits `POST /api/v1/ai/tasks` with an optional `idempotency_key`.
2. **Immediate Acknowledgment**: API enqueues the task in background workers and returns `HTTP 202 Accepted {"id": "task-uuid", "status": "QUEUED"}`.
3. **Live Streaming**: Client connects to `GET /api/v1/ai/tasks/{task_id}/stream` (`text/event-stream`) to receive live state transitions, incremental progress events, and final output payloads.

---

## 🛡️ 5. Security & Multi-Tenant Data Isolation

- **Authentication**: Validates RS256 JSON Web Tokens minted by Clerk against public JWKS endpoints with a 5-minute cache.
- **Tenant Isolation**: Every database operation enforces `Project.user_id == current_user.id` or verifies parent project ownership.
- **Configuration Security**: `Settings.validate_production_config()` enforces fail-fast validation in production mode, blocking SQLite, wildcard CORS, or missing issuers.

---

## 🧪 6. Architectural Fitness Functions

Automated architectural constraints are enforced in CI via `apps/api/tests/test_architecture_fitness.py`:

- **Layer Direction**: Lower layers (`core`, `models`, `schemas`, `db`) never import from `api.routes`.
- **Engine Purity**: `DeterministicEvaluationEngine` has 0 database, network, or external LLM dependencies.
- **Schema Standards**: All schemas use Pydantic v2 `ConfigDict` with 0 legacy `class Config:`.
- **Tenant Scoping**: Domain services require explicit `user_id` or `User` parameters.

---

## 📚 7. Architecture Decision Records (ADRs)

- [ADR-0001: Architecture Monorepo Setup](./ADR/0001-architecture.md)
- [ADR-0002: Deterministic Evaluation Engine & State Machine](./ADR/0002-deterministic-evaluation-engine.md)
- [ADR-0003: Clerk RS256 JWKS Key Verification & Multi-Tenancy](./ADR/0003-clerk-rs256-jwks-and-multi-tenancy.md)
- [ADR-0004: Multi-Provider Dynamic Discovery & AI Routing](./ADR/0004-multi-provider-dynamic-discovery-routing.md)
- [ADR-0005: Modular Monolith and Service Boundaries](./ADR/0005-modular-monolith-and-service-boundaries.md)
