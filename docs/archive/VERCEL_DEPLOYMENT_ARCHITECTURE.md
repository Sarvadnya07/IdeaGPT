# IdeaGPT — Vercel Deployment Architecture

## Architecture Overview
IdeaGPT is configured for high-performance deployment on Vercel leveraging:
1. **Next.js 16 Frontend**: Running on Vercel Edge / Serverless with React 19, Turbopack, and automatic static optimization (21 routes).
2. **FastAPI Backend Service**: Exposed via `@vercel/python` runtime through `apps/api/index.py`, utilizing ASGI async execution, dynamic connection pooling, and Clerk RS256 JWKS authentication.
3. **Monorepo Structure**: Managed via pnpm workspaces and Turborepo with root `vercel.json` orchestration.

## Routing & Proxy Model
- Frontend requests to `/api/v1/:path*` can either:
  - Route directly to an external API origin (`NEXT_PUBLIC_API_URL=https://api.ideagpt.com/api/v1`), OR
  - Route same-origin via Next.js rewrites (`INTERNAL_API_URL` or `FASTAPI_URL`), eliminating cross-origin CORS overhead.
