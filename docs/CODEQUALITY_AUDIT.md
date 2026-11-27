# CODEQUALITY-01 — Code Quality, Maintainability & Architecture Audit

**Project:** IdeaGPT (Turborepo monorepo: Next.js `apps/web`, FastAPI `apps/api`)
**Date:** 2026-09-14
**Scope:** Audit-only. No refactoring performed.
**Method:** Direct inspection of implementation (not filenames): backend app (~18.2k LOC Python), frontend (~20.3k LOC TS/TSX), tests (~8.3k LOC pytest + Vitest/Playwright), CI, docs, ADRs, static-analysis config.

---

## Executive Code Quality Assessment

**Verdict: This codebase is genuinely easy to understand and safely change for its maturity stage — well above typical MVP quality — but it carries three structural risks that will compound if unaddressed: (1) a growing orchestrator god-module, (2) hardcoded "insight" fabrication that quietly mixes synthetic data into user-facing analytics, and (3) duplicated knowledge between `EvaluationCoordinator` and a pass-through `EvaluationService` layer.**

The backend shows unusually strong discipline for a project of this size: real architecture fitness tests that run in CI, explicit FSMs with stale-job recovery, fail-closed security config, honest provenance tagging of AI output, and an honestly-labeled `SIMULATED_DEMO_DATA` benchmark. The frontend is functional and consistently built but has a page-component bloat problem and heavy `any` usage at API boundaries.

**Maturity classification:** **Growing Product** transitioning toward **Production**. CI gates, architecture tests, and ADRs exist; what's missing is debt visibility records, typing depth at boundaries, and consistent data provenance in domain services.

---

## Project Maturity

| Stage criteria (Growing Product) | Status |
|---|---|
| Consistency | ✅ Strong backend; ⚠️ frontend pages diverge in style |
| Modularity | ✅ Layered backend (core/models/schemas/api/services/evaluation/ai) |
| Debt visibility | ⚠️ Partial — no debt register; stale-ness hides in large modules |
| CI gates | ✅ pytest, alembic drift check, tsc, vitest, build, CodeQL, pip-audit (⚠️ audits `|| true` — non-blocking) |

Enterprise ceremony is appropriately *not* imposed. This is correct calibration.

---

## Architecture Map

```
apps/web (Next.js 16)                 apps/api (FastAPI)
├─ app/(dashboard)/*  [pages]         ├─ core/        config, security, rate limit, db
├─ hooks/*            [React Query]   ├─ db/          session
├─ lib/api/           [client+errors] ├─ models/      SQLAlchemy 2.0 entities
├─ store/             [zustand]       ├─ schemas/     Pydantic v2 DTOs
└─ e2e/               [Playwright]    ├─ api/routes   HTTP layer
                                      ├─ services/    domain services (18)
packages/ui, typescript-config        ├─ evaluation/  FSM coordinator + executor + engine
                                      ├─ ai/          gateway + orchestrator + providers
                                      └─ workers/     background tasks
```

Responsibilities are correctly placed. Routes are thin (delegation), services own domain logic, the deterministic engine is pure (verified by a fitness test), and AI concerns are isolated in `ai/`. The `apps/api/api/index.py` + `index.py` duplication exists for Vercel sys.path bootstrapping — intentional, should be documented.

---

## Dependency Direction

**Assessment: Healthy. No cycles detected in the layers reviewed.**

- `core`, `models`, `schemas`, `db`, `services` do **not** import `app.api.routes` — enforced by `test_dependency_direction_core_and_models_do_not_import_routes` (AST-based).
- Legacy `app.ai.providers` is confined to `ai/orchestrator/` — enforced by test.
- `DeterministicEvaluationEngine` purity enforced by AST test.

Findings:
- **F-01** Services import `fastapi.HTTPException` directly (e.g. `coordinator.py`, `insight_service.py`). Domain layer coupled to the HTTP framework. Low severity for a modular monolith, but it makes future non-HTTP reuse (workers/CLI) carry FastAPI. *Signal only — do not fix speculatively.*
- **F-02** `main.py` lifespan does function-level imports (`from app.core.database import engine` inside the function). Deliberate lazy-import to control startup order; acceptable, but it hides real dependencies from readers. A one-line comment would resolve the ambiguity.
- **F-03** `services/evaluation_service.py` and routes contain *deferred* imports inside request handlers (e.g. `global_search`, orchestrator imports in `ops.py`). Consistent pattern, but adds hidden coupling and makes import-graph tooling less useful.

---

## Cohesion

- `core/` — good functional cohesion. `config.py` is large but singularly about settings.
- `evaluation/coordinator.py` — **high functional cohesion**; one lifecycle, well named.
- `services/analytics_service.py` (456 LOC) — divergent change risk: user analytics, AI usage gauge, activity feed, venture matrix, provider telemetry, cache telemetry, system health all in one class. These change for different reasons (product analytics vs ops telemetry). **Candidate for split into `analytics_service` + `telemetry_service` when one of them next changes.** Not urgent.
- `ai/orchestrator/orchestrator.py` (942 LOC) — **god module.** One class holds: the evaluation pipeline, generic dynamic-tool generation, and nine lab generators (roadmap, tech-stack, architecture, PRD, pitch deck, github, investor, mentor, recruiter, strategy), each embedding a massive inline fallback payload (hundreds of lines of hardcoded demo content). See F-05.
- `main.py` — moderate: health endpoints + metrics + CORS + routers in one file. Acceptable at this size (233 LOC).

---

## Coupling

- Service layer uses explicit parameter passing (`db`, `user_id`) — good data coupling, no hidden globals except module singletons (`evaluation_service = EvaluationService()`, `orchestrator`, `gateway_registry`, module-level `_jwks_client`). Singletons are conventional and effectively immutable-in-behavior; acceptable.
- **F-04 (Global mutable settings as test seam):** `test_architecture_fitness.py` mutates `settings.APP_ENV`/`settings.CREDENTIAL_ENCRYPTION_KEY` directly with a try/finally restore. This is hidden shared mutable state in tests — a parallel test run or a future async test could interleave. Prefer monkeypatch fixture.
- HTTPException-based control coupling between service and route layers (see F-01).
- `EvaluationService` duplicates coordinator's method surface 1:1 (see F-07) — inappropriate intimacy without value.

---

## Public / Internal Boundaries

- Backend public surface = routers; internal = services. **Not formally enforced** (no `__all__` discipline in services, no import-linter). The architecture fitness tests partially cover direction but not export surface.
- Frontend `lib/api` is a clean public boundary (client, errors, dev-token) with unit tests — exemplary small module design.
- `apps/web/lib` only contains `api/`, `env.ts`, `utils.ts` — good restraint; no utility dumping ground.

---

## Readability / Naming

**Strengths:** Domain language is consistent and precise (`EvaluationCoordinator`, `verify_idea_ownership`, `recover_stale_evaluations`, `record_history_event`, `read_execution_provenance`). Test-mode naming is explicit (`_verify_test_token`). The provenance vocabulary (`DETERMINISTIC_CALCULATION`, `LIVE_SYSTEM_TELEMETRY`, `SIMULATED_DEMO_DATA`) is an honest, excellent convention.

**Findings:**
- **F-05** `orchestrator.py` fallback functions like `fallback_fn()` return 100+ line hardcoded dicts (investor cap tables, mentor personas, recruiter JDs). These are content, not code — they bury the actual control flow. Move to data modules (`app/ai/prompts/fallbacks/` or JSON) so the orchestrator reads as logic.
- **F-06** Frontend `result_payload: any` (in `useEvaluation.ts`) and `rawData: any` in the analysis page: the *central domain object* of the product is untyped. Typing `EvaluationResult` once would eliminate ~10 downstream `any`s.
- Minor: `first_arg`/`second_arg` in `AiTaskService.execute_task` is an honest but awkward dual-signature shim; a comment explains it — acceptable transitional debt.

---

## Comments

Overall high quality — this codebase comments *why*, not *what*:
- ✅ `security.py` module docstring documents fail-closed rules and test-mode isolation — exactly right.
- ✅ `config.py` Clerk block explains issuer derivation and explicitly warns where `CLERK_SECRET_KEY` should *not* go.
- ✅ `orchestrator.generate_roadmap_ai_with_provenance` documents *why* provenance travels with the result (a past misreport bug).
- ⚠️ `coordinator.list_project_evaluations`: comment "scalars().all() returns a Sequence; convert to list to satisfy return type" is stated twice in one method (lines for res_evals and the return) — one is redundant.
- No stale TODO/FIXME/HACK markers found anywhere — notable and good.

---

## Functions / Methods

- `DeterministicEvaluationEngine.evaluate` (~180 LOC) is long but **linear, single-purpose, and readable** — this is the acceptable kind of long function. Splitting it would add navigation overhead without clarity. *Keep.*
- `orchestrator.analyze_startup_idea` mixes context resolution, routing, caching, invocation, repair, and fallback in one method — justified by pipeline cohesion, borderline.
- Route handlers are uniformly thin. Route file LOC limit (400) enforced by fitness test; `ai/ops.py` at 351 is close to the ceiling and contains 5 near-identical generator endpoints (see F-09).
- `AiTaskService._execute_task_internal` has four nearly identical exception handlers (F-10).

---

## Classes / Modules

- No god objects in the domain layer; `EvaluationCoordinator` (classmethod namespace) is well scoped.
- `AIOrchestrator` is the one true god class (F-05).
- `AnalyticsService` mixes two concern clusters (F-11).
- `Settings` config class: large but coherent; properties are well-factored.

---

## Complexity

Essential vs accidental:
- **Essential:** FSM transition logic, JWKS verification branches, multi-provider fallback routing. All justified.
- **Accidental:** (a) orchestrator's per-lab prompt+fallback boilerplate (F-05/F-09), (b) duplicated export endpoints (`/evaluations/{id}/export` vs `/exports/json` vs `/exports/markdown` — three routes for the same operation), (c) the four clone error handlers in `ai_task_service`.
- Metrics signals: no function exceeds understandability thresholds except orchestrator methods; nesting stays shallow (≤4) throughout the sampled code.

---

## Code Smells

| Smell | Location | Material? |
|---|---|---|
| Large Class | `AIOrchestrator` (942 LOC) | Yes — F-05 |
| Duplicated Code | `/exports/json` + `/exports/markdown` + `/evaluations/{id}/export` | Yes — F-08 |
| Duplicated Code | 4× `except` blocks in `_execute_task_internal` | Minor — F-10 |
| Divergent Change | `AnalyticsService` | Yes — F-11 |
| Duplicated Code | 5× near-identical lab endpoints in `ops.py`/`labs.py` (save_artifact + provenance dance) | Medium — F-09 |
| Magic Values | Dimension weights `0.20/0.15...` in engine; default scores `70`, `75` sprinkled in services | Minor |
| Dead Code / Speculative Generality | `generate_roadmap_ai` / `generate_pitch_deck_ai` backward-compat wrappers | Verified used by tests; fine for now |
| Lying Comments | None found | — |

---

## Abstractions

- **Stable & justified:** `BaseProviderAdapter` + `gateway_registry` (multiple real implementations: groq, gemini, openai, ollama, tavily + mock), `AIRouter`, `DeterministicFallback` (single auditable fallback path, enforced by fitness test), `EvaluationExecutor` tx-boundary split.
- **Borderline:** `EvaluationService` as a pure delegation shim (F-07) — the abstraction adds a second name for every coordinator method. Justified only if it ever gains its own logic (it has one: `diff_evaluations` — which suggests the split is *starting* to earn its place; consider moving `diff_evaluations` into the coordinator instead and deleting the shim later).
- **No interface explosion:** services are concrete classes; no DI container; no interfaces-for-mocks. Good restraint.

---

## Duplication

- **Knowledge duplication (fix-worthy):** export endpoints (F-08); lab-endpoint artifact-saving ritual (F-09); AI task error handlers (F-10).
- **Intentional/textual (leave alone):** the four provider adapters are structurally similar but encode genuinely different vendor protocols — do *not* merge.
- **F-12:** `index.py` and `api/index.py` are byte-identical Vercel bootstrap files. Intentional (two entry-point resolutions); add a comment in each pointing at the twin to prevent future drift.

---

## SOLID

- **SRP:** Good in domain layer; violated in `AIOrchestrator`, drifting in `AnalyticsService`.
- **OCP:** Provider registry achieves it concretely (new provider = new adapter + registration). Good.
- **LSP:** Adapter hierarchy honors `execute`/`health` contract; fitness test checks substitutability. Good.
- **ISP:** No interface bloat. Good.
- **DIP:** Services depend on concrete coordinator (fine for a monolith); the adapter layer protects the boundary that actually varies (LLM vendors). Correct prioritization.

No cargo-culting detected. This is the right amount of SOLID.

---

## Composition / Inheritance

Inheritance used only for provider adapters (genuine subtype contract). Everything else is composition/classmethod namespaces. No fragile base classes observed. Healthy.

---

## Error Handling

**Strengths:**
- `core/exceptions.py` centralizes handlers; typed AI exception hierarchy (`AIException`, `AIUnavailableException`, `AIQuotaExceededException`) with user-safe messages — exemplary.
- Security errors fail closed with distinct 401 vs 500 semantics; `WWW-Authenticate` headers present.
- Frontend `normalizeApiError` is a pure, unit-tested error→message policy. Excellent.

**Findings:**
- **F-13 (Silent excepts):** 20 bare `except Exception:` / `except Exception: pass` sites in production code, including: `main.py` metrics DB query (`except Exception: pass` — returns fake zero-count metrics on DB failure with no signal), `engine.dispose()` shutdown (acceptable), `config.async_database_url` (falls back to raw URL — hides malformed DATABASE_URL). Each should either log or narrowly catch. The `/metrics` one is the most concerning: monitoring silently lies when the DB is down.
- **F-14:** `insight_service.py` / `ScoringService.get_scores` do not re-verify tenant ownership when called directly — the *routes* call `evaluation_service.get_evaluation` first (ownership check) then the service. Defense rests on caller discipline; the fitness test checks signatures, not call ordering. Medium risk of a future route forgetting the ownership pre-check.
- Error context: fallback warning logs include provider name and exception — good.

---

## State / Side Effects

- Module-level singletons (`evaluation_cache`, `gateway_registry`, `_jwks_client`, service instances) — predictable, conventional.
- **F-15 (Temporal coupling):** `EvaluationService.trigger_evaluation` commits, then calls `run_evaluation` which commits again then executes; `create_evaluation` itself commits internally. Commits are spread across three layers; a reader must trace three files to know transaction boundaries. The executor's "isolated transaction" design (ADR-0002) is sound, but the create/commit/refresh/re-commit sequence is accidental complexity.
- **F-16:** `insight_service.get_insights` builds `risk_analysis` from **hardcoded static content** while claiming to derive from evaluation data. TAM/SAM/SOM figures are one conditional + canned strings. This is fabricated analysis presented as data (see Critical Gaps).

---

## Concurrency

- **Good:** `EvaluationConcurrencyConflictError`, active-evaluation uniqueness guard (409), stale RUNNING recovery on startup, stale task sweeper with explicit timeout, `VALID_STATUS_TRANSITIONS` FSM for tasks and evaluations.
- **F-17 (Check-then-act race):** `create_evaluation`'s "single active evaluation per idea" is a SELECT-then-INSERT without a DB constraint or `SELECT ... FOR UPDATE`. Two concurrent POSTs can both pass the check and create duplicate active evaluations. Impact: low at current scale; a partial unique index (`idea_id WHERE status IN ('PENDING','RUNNING')`) would make it structural. Same pattern in idempotency check in `AiTaskService.create_task` (dedupe by select-then-insert).
- Background task execution is in-process (FastAPI BackgroundTasks); SSE streaming present. No deadlock risks observed; no shared mutable state across requests beyond registries.

---

## Testability

**Strong.** 35 backend test modules incl. architecture fitness, security hardening, contract consistency, environment contract; frontend Vitest unit tests for pure modules; Playwright e2e incl. tenant isolation. Deterministic engine is pure → trivially testable. Test-mode HS256 token path is cleanly isolated and asserted.

Gaps:
- No coverage measurement configured in CI (coverage not reported or gated).
- E2E tenant test mocks the API with tenant-filtered route handlers — it validates the *UI's* handling of isolation, not the backend's. The backend isolation tests exist separately (auth, security hardening); the layered approach is fine but the e2e test name could mislead.
- No characterization tests before the planned orchestrator refactor (see Roadmap).

---

## Types

- Backend: mypy configured but weak (`check_untyped_defs = false`, `ignore_missing_imports = true`, `warn_return_any = false`) — **typecheck is theater, not a gate.** Pydantic v2 schemas carry the real typing weight at boundaries, which is acceptable, but internal drift (e.g., `dict` payloads) is unpoliced.
- Frontend: strict TS config; but 23 `any` usages in hooks/app, concentrated exactly on API response shapes (`result_payload: any`). The typed core is undermined at the most changed boundary.

---

## Configuration

**Excellent.** Single `Settings` source; env-var precedence standard; fail-fast production validation (SQLite ban, wildcard CORS ban, mandatory encryption key, test-secret ban); `get_config_status()` exposes booleans not values; secrets never logged. `.env.example` files present. Minor: default `DATABASE_URL` sqlite fallback in dev is fine and documented.

---

## Dependencies

Pinned exact versions (pyproject) — deterministic builds. `pip-audit` and `pnpm audit` run but with `|| true` (non-blocking) — intentional to avoid false-positive toil; flag as a policy decision to revisit when the product hardens. No unnecessary deps spotted in the sampled import graph (e.g., `passlib`, `structlog`, `tenacity` present — verify usage if pruning later; low priority).

---

## Organization

- Backend: exemplary feature locality. `ai/gateway` subpackages (strategy/execution/evidence/providers/security) are discoverable and cohesive.
- Frontend: page components are 300–1130 LOC monoliths (analysis page = 1130 lines containing InsightModule, radar chart math, export logic, form steps, model selector). F-18: extract per-section components *when next touched*; the radar chart and insight modules are natural seams. Do not do a wholesale split.
- `apps/api/api/index.py` + `index.py` twins: document (F-12).

---

## Architecture Fitness

**This is the standout strength.** 13 automated fitness functions in CI verify: dependency direction, engine purity, Pydantic v2 conformity, tenant-scoping signatures, fail-closed config, SSE contract, route LOC limits, adapter registry health, bounded state caps, provider gateway authority, legacy-package confinement, single deterministic fallback path, credential-key enforcement. Architecture is *continuously enforced*, not just documented. ADR-0001…0005 document decisions with rationale.

Weakness: fitness tests check signatures/imports, not behavior (ownership enforcement is signature-level, per F-14).

---

## Code Generation

No codegen present. `export_openapi.py` + committed `openapi.json` provide a contract artifact — good for contract-consistency testing (`test_contract_consistency.py` exists).

---

## Legacy

- `app.ai.providers` (legacy provider package) is deprecated and confined by fitness tests; orchestrator compatibility factory bridges it. Clear strangler pattern in progress. Keep the retirement tracked — it's the one migration without a documented end-state.
- `AiTaskService.execute_task(first_arg, second_arg=None)` dual-signature — transitional legacy shim, acknowledged in code.

---

## Refactoring Risk

| Area | Tests guarding? | Risk to refactor |
|---|---|---|
| Deterministic engine | ✅ multiple | Low |
| Coordinator/FSM | ✅ sprint2_6, feature tests | Low |
| Orchestrator labs | ✅ sprint5/phase tests | **Medium — write characterization tests on fallback payloads first (F-19)** |
| Analytics | ✅ sprint8_3 | Low–Medium |
| Auth/security | ✅ dedicated suites | Low |

---

## Technical Debt Register

| ID | Debt | Type | Interest | Class |
|---|---|---|---|---|
| F-05 | Orchestrator god module + inline fallback content | Architecture | High (every new lab makes it worse) | Prudent-turned-reckless if unbounded |
| F-16 | Hardcoded insight/TAM data presented as analysis | Correctness/Trust | High | Reckless (misleads users) |
| F-17 | Check-then-act race in eval creation/idempotency | Code | Medium | Accidental |
| F-07 | EvaluationService delegation shim | Design | Low | Prudent (mid-migration) |
| F-08/F-09/F-10 | Route/handler duplication | Code | Medium | Accidental |
| F-13 | Silent excepts incl. /metrics | Observability | Medium | Accidental |
| F-18 | 1100-line page components | Code | Medium | Prudent |
| F-06 | `any` at API boundary types | Testing/Types | Medium | Accidental |
| — | No coverage gate | Testing | Medium | — |
| — | Legacy provider retirement unfinished | Architecture | Low | Intentional |

---

## Code Review / PR Locality

Cannot inspect review history from this audit; repo shows 4 merged PRs, 129 commits, single human + bot contributor. CI + fitness tests substitute for much review discipline. Pre-commit hook runs lint only — fast, correct choice.

---

## Static Analysis & Quality Gates

- ESLint with nearly all rules off (`no-unused-vars: off`) — **lint is effectively decorative on the frontend.** Enable `@typescript-eslint/no-unused-vars` at minimum.
- Flake8 referenced in docs/CONTRIBUTING but no config file found in repo — verify it actually runs (`pnpm lint` claims Flake8; no `.flake8`/setup.cfg present → likely silently no-op).
- mypy too permissive to be meaningful (see Types).
- Prettier + husky present. CI gates solid except audits and coverage.

---

## Metrics

Metrics culture is healthy: LOC caps enforced only where they encode a real rule (routes), provenance labels prevent vanity telemetry (`uptime_pct` forbidden by test unless live). No metric gaming observed.

---

## Performance / Maintainability Interaction

Analytics service loads all projects/ideas/evaluations into Python for aggregation instead of SQL aggregation — fine at current scale, will degrade with data volume. This is acceptable essential simplicity *now*; note as a scaling watch-point, not a defect. No unjustified "optimization" complexity found.

---

## Anti-Patterns

Present (mild): god class (orchestrator), silent exception swallowing, untyped boundary payloads, check-then-act persistence.
Absent (notably): speculative generality, interface explosion, DI ceremony, utility dumping grounds, lying comments, global mutable config, magic-string status chaos (FSMs are enum-driven).

---

## Decision-Tree Findings

- **Refactor orchestrator now?** Pain: yes (growth per lab). Risk: manageable. Guard: write characterization tests on fallback payload shapes first (F-19). → **Yes, incrementally.**
- **Deduplicate export endpoints?** Same knowledge, three routes, changing together → **Yes (F-08).**
- **Introduce interfaces for services?** Single implementations, no variants imminent → **No.**
- **Split AnalyticsService?** Only when one half next changes → **Defer (F-11).**
- **Fix insight fabrication (F-16)?** Correctness/trust issue on a user-facing surface → **Do now.**
- **Enforce eval-uniqueness in DB?** High-churn path, correctness risk → **Do soon (F-17).**

---

## Strengths Worth Preserving

1. The architecture fitness test suite — rare and valuable; extend, never let it rot.
2. Provenance honesty conventions (`SIMULATED_DEMO_DATA`, `DETERMINISTIC_CALCULATION`).
3. Fail-closed security posture with test-mode isolation that is structurally impossible in production.
4. Pure deterministic engine as the universal fallback.
5. Comment discipline: why-focused, no stale TODOs.
6. Frontend error normalization as a tested pure function.

---

## Critical Gaps

1. **F-16 — Fabricated analytics:** `insight_service` (TAM/SAM/SOM, risk matrices) and `analytics_service.get_ai_usage_gauge` ("daily_average_tokens" = tokens/30 regardless of actual window) present canned or naïvely-derived numbers as data. Combined with honest-provenance labeling elsewhere, this is an internal inconsistency that can mislead users and erode the product's core trust proposition.
2. **F-05 — Orchestrator growth curve:** each new lab adds ~80–120 LOC of prompt + fallback to one class; the 942-line file is at the knee of the curve.
3. **Type/coverage gates are shallow:** mypy no-ops, ESLint no-ops on the frontend, no coverage signal — the gates that exist are excellent, the missing ones are the cheap ones.

---

## Prioritized Roadmap

**DO NOW (high interest, low remediation cost)**
1. F-16: Label all derived/canned insight fields with provenance; compute or clearly mark estimates. *(~1 day)*
2. F-13: Add logging to silent excepts; `/metrics` must not return fake zeros on DB failure. *(hours)*
3. F-08: Collapse `/exports/json`, `/exports/markdown` into the canonical export route. *(hours)*
4. Enable `no-unused-vars` (TS) and confirm Flake8 actually executes; add a real config. *(hours)*

**PLAN (next 1–2 sprints)**
5. F-19 → F-05: Characterization tests over all lab fallback payloads, then extract fallback content to data modules and split orchestrator into `evaluation_pipeline` + `tool_generators`.
6. F-17: Partial unique index for active evaluations + `ON CONFLICT` handling for idempotency.
7. F-06: Type `EvaluationResultPayload` (discriminated per provider) and propagate through hooks; drop `result_payload: any`.
8. Add coverage reporting to CI with a trend (no hard gate initially).

**CONTAIN (accept with controls)**
9. F-14: Document the ownership-check contract between routes and insight/scoring services; add one behavioral tenant test.
10. F-11: Split AnalyticsService on next touch.
11. F-18: Extract components from the analysis page opportunistically.
12. F-12/F-02: Comments documenting entry-point twins and lazy-import rationale.

**IGNORE / ACCEPT**
- Service→HTTPException coupling (F-01), Analytics in-Python aggregation, commit sequencing granularity (F-15) until scale or reuse demands differ.

---

*Audit performed per audit-first protocol: no production code was modified.*
