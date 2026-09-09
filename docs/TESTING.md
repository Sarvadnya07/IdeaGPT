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

# Run a specific backend test module
pnpm --filter api test -- tests/test_health.py -v
```

---

## ⚖️ Database Parity: SQLite vs PostgreSQL

IdeaGPT utilizes a two-tier database testing strategy:

### Tier 1: Fast In-Process Unit Tests (SQLite)
* **Configuration:** `conftest.py` sets `DATABASE_URL = sqlite+aiosqlite:///./test.db`.
* **Purpose:** Enables rapid local developer feedback loops (250+ backend tests run in under 25 seconds).
* **Isolation:** Automatic table creation and teardown per test via async session fixtures.

### Tier 2: Real Database Integration Tests (PostgreSQL 15 / 18.4)
* **Configuration:** Used in GitHub Actions CI (`.github/workflows/ci.yml`) and local PostgreSQL validation scripts (`scratch/verify_pg_sprint2_3.py`, `scratch/verify_pg_sprint2_4.py`).
* **Critical Areas Tested Against PostgreSQL:**
  1. **Foreign Key `ON DELETE CASCADE`:** Tested to ensure deleting projects cascades to ideas in PostgreSQL.
  2. **JSONB & Complex Serialization:** Payload validation for AI evaluation results.
  3. **Case-Insensitive Searching (`ILIKE` / `func.lower`):** Global search queries across titles and tags.
  4. **Alembic Schema Drift:** `alembic check` runs against PostgreSQL service in CI to guarantee 100% migration parity.

---

## 🔒 Authentication in Tests

* Backend tests run with `APP_ENV=test` and `CLERK_JWT_TEST_SECRET`.
* This activates deterministic token minting without calling external Clerk servers.
* No live Clerk credentials or network access are required to execute the test suites.
