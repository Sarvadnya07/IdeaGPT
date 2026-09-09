# IdeaGPT — Vercel & Turborepo Environment Variable Scoping Audit

## Root Cause Analysis
During monorepo deployments on Vercel:
1. Vercel exposes all project-level environment variables (both frontend keys and backend secrets) to the build runner process that executes `turbo build`.
2. Turborepo scans `process.env`. If variables exist in the runner environment that are not accounted for in `turbo.json`, Turborepo issues warnings stating that variables are missing from `turbo.json`.
3. Indiscriminately adding backend secrets (e.g. `DATABASE_URL`, `GROQ_API_KEY`, `OPENAI_API_KEY`, `CLERK_SECRET_KEY`) into `globalEnv` or `tasks.build.env` would violate security boundaries by invalidating frontend cache on backend secret rotations and risking accidental exposure.

## Engineering Remediation
1. **Task-Specific Build Hashing (`tasks.build.env`)**:
   Only variables that legitimately affect Next.js compilation, client configuration, and routing are placed in `tasks.build.env`:
   - `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` (Public frontend auth key)
   - `NEXT_PUBLIC_API_URL` (Public API target)
   - `INTERNAL_API_URL` / `FASTAPI_URL` (Server-side Next.js rewrite targets)
   - `ANALYZE`, `BUILD_STANDALONE`, `DOCKER_BUILD` (Next.js build control flags)
2. **Global Pass-Through Scope (`globalPassThroughEnv`)**:
   Backend runtime secrets, rate-limiting configs, and platform variables are declared under `globalPassThroughEnv`. This allows Turborepo to acknowledge their presence in the Vercel runner without injecting them into the `web#build` hash or exposing them to client-side bundles:
   - Database: `DATABASE_URL`, `REDIS_URL`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`
   - AI Providers: `GROQ_API_KEY`, `GROQ_BASE_URL`, `GROQ_DEFAULT_MODEL`, `ENABLE_GROQ`, `OPENAI_API_KEY`, `ENABLE_OPENAI`, `GEMINI_API_KEY`, `ENABLE_GEMINI`, `ENABLE_OLLAMA`, `OLLAMA_URL`, `CUSTOM_PROVIDER_URL`, `CUSTOM_PROVIDER_KEY`, `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`
   - Auth: `CLERK_SECRET_KEY`, `CLERK_JWT_ISSUER`, `CLERK_AUTHORIZED_PARTY`, `CLERK_JWT_TEST_SECRET`, `CLERK_PUBLISHABLE_KEY`
   - Configuration: `APP_ENV`, `PROJECT_NAME`, `VERSION`, `CORS_ORIGINS`, `RATE_LIMIT_*`
   - Platform: `VERCEL`, `VERCEL_ENV`, `VERCEL_URL`, `CI`

## Verification Matrix
- **Secret Leak Test**: Inspected `.next` static and server JS bundles with regex searches for backend secrets; 0 secrets exposed.
- **Turborepo Build**: Tested with simulated Vercel environment variables; 0 warnings emitted.
- **Full Suite Regression**: 228 Pytest tests passed, 30 Vitest tests passed, 19 Playwright tests passed, Flake8 clean, Alembic clean, Docker build clean.
