# IdeaGPT — Vercel Environment Variables Reference

## Target Environments: Production, Preview, Development

| Variable Name | Scope | Target Environments | Purpose |
|---|---|---|---|
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Public | Production, Preview, Dev | Clerk frontend authentication initialization |
| `CLERK_SECRET_KEY` | Private (Backend) | Production, Preview, Dev | Clerk backend management & token sync |
| `CLERK_JWT_ISSUER` | Private (Backend) | Production, Preview, Dev | Clerk RS256 JWKS verification issuer URL |
| `DATABASE_URL` | Private (Backend) | Production, Preview, Dev | PostgreSQL database connection string (`postgresql+asyncpg://...`) |
| `NEXT_PUBLIC_API_URL` | Public | Production, Preview, Dev | Frontend API base URL (`https://api.ideagpt.com/api/v1` or `/api/v1`) |
| `INTERNAL_API_URL` | Private (Frontend) | Production, Preview | Destination for Next.js same-origin `/api/v1/*` rewrites |
| `GROQ_API_KEY` | Private (Backend) | Production, Preview, Dev | Primary LPU inference key |
| `GEMINI_API_KEY` | Private (Backend) | Production, Preview, Dev | Optional multimodal inference key |
| `TAVILY_API_KEY` | Private (Backend) | Production, Preview, Dev | Optional deep research key |
| `APP_ENV` | Private | Production (`production`), Preview (`preview`), Dev (`development`) | Runtime environment classifier |
