# IdeaGPT — Docker Database Driver & Async Runtime Resolution

## Problem Description
During container startup with standard PostgreSQL connection strings (`postgresql://...` or `postgres://...`), the application failed with:
```
sqlalchemy.exc.InvalidRequestError: The asyncio extension requires an async driver to be used. The loaded 'psycopg2' is not async.
```
Additionally, `aiosqlite` was absent from `requirements.txt` for local development and fallback defaults, and the Docker build context size was approximately 124 MB due to missing `.dockerignore` files.

## Root Cause Analysis
1. **Driver Resolution**: In SQLAlchemy, standard PostgreSQL URLs starting with `postgresql://` or `postgres://` or `postgresql+psycopg2://` default to the synchronous `psycopg2` DBAPI driver. When passed to `create_async_engine()`, SQLAlchemy rejects synchronous drivers and raises `InvalidRequestError`.
2. **Distinct Driver Requirements**:
   - **Application Runtime (FastAPI)**: Requires asynchronous execution via `asyncpg` (`postgresql+asyncpg://...`) or `aiosqlite` (`sqlite+aiosqlite://...`).
   - **Database Migrations (Alembic)**: Requires synchronous execution via `psycopg2` (`postgresql+psycopg2://...`) or synchronous SQLite (`sqlite://...`).
3. **Docker Build Context**: Lack of `apps/api/.dockerignore` resulted in local virtual environments (`venv/`), database files (`*.db`), and caches being copied into the build context (~124 MB) and baked into the image.

## Engineering Remediation
1. **Config Normalization Properties**:
   - Added `async_database_url` on `Settings` in `app/core/config.py` using SQLAlchemy's `make_url` to robustly normalize `postgresql://`, `postgres://`, and `postgresql+psycopg2://` into `postgresql+asyncpg://`, preserving passwords, percent-encoding, ports, SSL flags, and parameters.
   - Added `sync_database_url` on `Settings` in `app/core/config.py` to normalize URLs for Alembic into `postgresql+psycopg2://`.
2. **Database Engine Integration**:
   - Updated `app/core/database.py` to initialize `create_async_engine(settings.async_database_url)`.
3. **Alembic Migration Preservation**:
   - Updated `alembic/env.py` to use `settings.sync_database_url` and safely escape `%` characters (`%%`) for Python's `configparser`.
4. **Dependency & Build Context Optimization**:
   - Added `aiosqlite==0.21.0` to `apps/api/requirements.txt`.
   - Created `apps/api/.dockerignore` and `.dockerignore`, reducing Docker build context transfer from 124 MB to 91 kB.

## Verification Matrix
- **Async Engine**: Verified `create_async_engine` loads `asyncpg` without errors.
- **Container Build**: `docker build -f apps/api/Dockerfile apps/api -t ideagpt-api:local` (Clean build, 91 kB context).
- **Container Startup**: `ideagpt-test` runs `uvicorn app.main:app` as non-root `appuser`.
- **Healthchecks**: `/health/live` (200), `/health/ready` (200), `/health/config` (401 protected).
- **Database Query**: Executed `SELECT 1` inside container using the application's actual async engine.
- **Alembic**: `python -m alembic check` verified with 0 drift.
- **Regression Suites**: 228 Pytest tests passed, 30 Vitest tests passed, 19 Playwright tests passed, Flake8 clean, Turborepo build clean.
