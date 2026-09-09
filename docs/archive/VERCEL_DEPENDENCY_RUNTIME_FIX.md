# IdeaGPT — Vercel Python Dependency & Entrypoint Resolution

## Root Cause Analysis
When deploying a monorepo from the root directory on Vercel:
1. Vercel's `@vercel/python` builder looks for `requirements.txt` in the root deployment directory.
2. Previously, `requirements.txt` only resided in `apps/api/requirements.txt`. Without a root `requirements.txt`, Vercel skipped dependency installation during the root build and immediately attempted to import `app/main.py`, resulting in:
   ```
   ModuleNotFoundError: No module named 'fastapi'
   ```
3. Furthermore, root serverless function discovery on Vercel requires a top-level `api/` directory (e.g. `api/index.py`) or path routing in `vercel.json`.

## Engineering Remediation
1. **Canonical Root Dependency Reference**:
   Created `requirements.txt` at the repository root referencing `-r apps/api/requirements.txt`. This guarantees that Vercel installs the complete IdeaGPT Python dependency set (FastAPI, SQLAlchemy, asyncpg, Pydantic, PyJWT, Cryptography, OpenAI, HTTPX, etc.) while preserving `apps/api/requirements.txt` as the single canonical source of truth.
2. **Dual-Entrypoint Architecture**:
   - **Root Entrypoint (`api/index.py`)**: Adds `apps/api` to `sys.path` and exports `app` from `app.main` for single-project monorepo deployments.
   - **Service Entrypoint (`apps/api/index.py`)**: Adds `apps/api` to `sys.path` and exports `app` for standalone backend deployments.
3. **Vercel Rewrites (`vercel.json`)**:
   Configured root `vercel.json` with rewrites mapping `/api/v1/:path*` and `/health*` to `/api/index.py`.

## Verification Matrix
- **Dependency Installation**: `pip install -r requirements.txt` executed at root installed all 44 dependencies.
- **Entrypoint Imports**: Both `api/index.py` and `apps/api/index.py` resolve and export `IdeaGPT API`.
- **Backend Pytest**: 228 passed.
- **Vitest & Playwright**: 30 Vitest tests and 19 Playwright tests passed.
- **Flake8 & Alembic**: 0 errors, 0 drift.
- **Docker**: `ideagpt-api:local` built cleanly.
