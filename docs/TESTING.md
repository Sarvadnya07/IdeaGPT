# 🧪 IdeaGPT Testing Architecture & Parity Guide

This guide details the test architecture, execution models, and environment parity across IdeaGPT.

---

## ⚡ Running Tests

### 1. Unified Test Execution (Recommended)

To run the complete test suite across both frontend and backend concurrently:

```bash
pnpm test
```

This runs:
* **Frontend:** Vitest unit & component test suite (`apps/web/tests/`).
* **Backend:** Pytest asynchronous test suite (`apps/api/tests/`).

### 2. Running Individual Test Suites

```bash
# Run only frontend Vitest tests
pnpm --filter web test

# Run frontend tests in watch mode
pnpm --filter web test -- --watch

# Run only backend Pytest tests
pnpm --filter api test

# Run PostgreSQL Integration Test Suite (real PostgreSQL 18.x)
pnpm test:integration

# Run Playwright End-to-End Browser Tests
pnpm test:e2e

# Run a specific backend test module
pnpm --filter api test -- tests/test_health.py -v
```

---

## 🐘 Tier 2: Real Database Integration Tests (`pnpm test:integration`)

The PostgreSQL integration suite (`apps/api/tests/integration/test_postgres_lifecycle.py`) verifies real PostgreSQL-specific behavior against PostgreSQL 18.4:

1. **Port & Connectivity Health Check:** Automatically verifies PostgreSQL 18 on port 5432.
2. **Alembic Migration Freshness:** Runs `alembic upgrade head` before test execution.
3. **Native PostgreSQL Constraints & Features:**
   * **Foreign Key `ON DELETE CASCADE`:** Project deletion cascades cleanly to child ideas and roadmaps without ORM nullification conflicts.
   * **Compound Unique Indexes:** Enforces `(user_id, provider)` unique constraint on `provider_credentials`.
   * **JSONB Milestone & Evaluation Persistence:** Validates complex structured JSON storage, retrieval, and schema integrity.
   * **Transaction Isolation & Rollback:** Verifies that uncommitted sessions leave PostgreSQL tables unmodified.

Execution:
```bash
pnpm test:integration
```

---

## 🎭 Tier 3: Playwright End-to-End Browser Automation (`pnpm test:e2e`)

Playwright runs deterministic, real browser automation against the Next.js frontend across 19 critical route and authentication scenarios:

* Public landing page accessibility
* Clerk `/sign-in` interface rendering
* Route protection & automatic redirection on unauthorized access (`/dashboard`, `/analytics`, `/compare`, `/roadmap`, `/settings`, `/tech-stack`, etc.)
* Automated Next.js dev server lifecycle orchestration

Execution:
```bash
pnpm test:e2e
```

---

## 🔒 Authentication in Tests

* Backend tests run with `APP_ENV=test` and `CLERK_JWT_TEST_SECRET`.
* This activates deterministic token minting without calling external Clerk servers.
* No live Clerk credentials or network access are required to execute the test suites.
