# 📚 IdeaGPT Documentation Master Index

Welcome to the IdeaGPT engineering documentation. This directory provides authoritative guides covering onboarding, daily development, architecture, testing, API contracts, deployment, and security.

---

## 🧭 Navigation Guide — What Should I Read First?

| Priority | Document | Target Audience | Description |
| :---: | :--- | :--- | :--- |
| **1** | [**SETUP.md**](./SETUP.md) | All Engineers | **Day 1 Quick Start:** Environment bootstrapping, prerequisites, and first-time setup via `pnpm setup`. |
| **2** | [**DEVELOPMENT.md**](./DEVELOPMENT.md) | All Engineers | **Daily Workflow:** Canonical commands (`dev`, `test`, `typecheck`, `lint`, `build`, `clean`), Docker, and debugging. |
| **3** | [**ARCHITECTURE.md**](./ARCHITECTURE.md) | Core & Platform | **System Blueprint:** Modular monolith boundaries, Next.js frontend, FastAPI backend, and AI Gateway. |
| **4** | [**TESTING.md**](./TESTING.md) | QA & Backend/Frontend | **Test Architecture:** Unified `pnpm test`, Vitest, Pytest, SQLite unit vs PostgreSQL integration test parity. |
| **5** | [**API.md**](./API.md) | Full-Stack & Integration | **API Guide:** RESTful endpoint catalog, Clerk RS256 JWT auth flow, OpenAPI schema export, and rate limits. |
| **6** | [**DEPLOYMENT.md**](./DEPLOYMENT.md) | DevOps & Release | **Deployment Guide:** Production containerization, Vercel frontend, Railway/Docker backend, and environment variables. |
| **7** | [**SECURITY.md**](./SECURITY.md) | Security & Platform | **Security Architecture:** Clerk RS256 JWKS verification, strict tenant isolation, and threat modeling. |
| **8** | [**OPERATIONS.md**](./OPERATIONS.md) | SRE & Operations | **Production Runbooks:** Observability, health endpoints (`/health`, `/health/ai`, `/health/config`), and recovery. |
| **9** | [**ADRs (`docs/adr/`)**](./ADR/) | Architects & Tech Leads | **Architecture Decision Records:** Historical rationale for deterministic evaluation, multi-provider AI, etc. |
| **10** | [**Archive (`docs/archive/`)**](./archive/) | Historical Reference | **Sprint & Audit Logs:** Preserved historical audit reports, sprint completions, and legacy verification artifacts. |

---

## ⚡ Canonical Golden Path Commands

```bash
# 1. First-time setup (idempotent bootstrap for Node, Python venv, and environment templates)
pnpm setup

# 2. Start full-stack development (Next.js at :3000, FastAPI at :8000)
pnpm dev

# 3. Run complete test suites (Frontend Vitest + Backend Pytest)
pnpm test

# 4. Run TypeScript static type verification
pnpm typecheck

# 5. Run linters across entire monorepo
pnpm lint

# 6. Build production bundles
pnpm build

# 7. Clean temporary build artifacts and test caches
pnpm clean
```
