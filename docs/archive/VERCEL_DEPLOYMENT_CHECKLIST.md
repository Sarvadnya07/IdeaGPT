# IdeaGPT — Vercel Deployment Checklist

## Pre-Deployment Setup
- [x] Create root `vercel.json` with Turborepo build command (`turbo build`).
- [x] Create `apps/api/vercel.json` and `apps/api/index.py` serverless Python entrypoint.
- [x] Configure serverless-aware database connection pooling in `apps/api/app/core/database.py`.
- [x] Configure Next.js rewrites in `apps/web/next.config.mjs` for same-origin proxying.
- [x] Ensure CSP in `apps/web/next.config.mjs` includes `https://*.vercel.app` and Clerk domains.

## Vercel Dashboard Configuration
1. **Import Repository**: Connect `https://github.com/Sarvadnya07/IdeaGPT`.
2. **Configure Frontend**: Set Root Directory to repository root or `apps/web`.
3. **Environment Variables**: Populate required production environment variables (see `docs/VERCEL_ENVIRONMENT_REFERENCE.md`).
4. **Database Migrations**: Run `python -m alembic upgrade head` prior to routing production traffic.
5. **Deploy & Validate**: Test `/health/live`, `/health/ready`, Clerk sign-in, project creation, and AI evaluation.
