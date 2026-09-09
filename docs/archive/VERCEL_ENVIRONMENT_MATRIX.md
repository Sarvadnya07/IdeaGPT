# IdeaGPT — Vercel Environment Variables Matrix

| Variable Name | Consumer | Scope | Type | Required in Prod | Purpose / Example |
| :--- | :--- | :--- | :--- | :---: | :--- |
| `APP_ENV` | Backend | Server | Config | **YES** | Set to `production` |
| `DATABASE_URL` | Backend | Server | Secret | **YES** | Async PostgreSQL connection: `postgresql+asyncpg://...` |
| `CLERK_PUBLISHABLE_KEY` | Backend | Server | Public Key | **YES** | Used to derive JWKS issuer (`pk_live_...` or `pk_test_...`) |
| `CLERK_SECRET_KEY` | Backend / SSR | Server | Secret | **YES** | Used by `clerkMiddleware` and backend operations (`sk_live_...`) |
| `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` | Frontend | Client | Public Key | **YES** | Client-side Clerk authentication widget |
| `NEXT_PUBLIC_API_URL` | Frontend | Client | URL | **YES** | Backend API origin (`/api/v1` or full URL) |
| `CORS_ORIGINS` | Backend | Server | Config | **YES** | Allowed CORS origins (`https://your-domain.vercel.app`) |
| `GROQ_API_KEY` | Backend | Server | Secret | **YES** | Groq LPU API Key (`gsk_...`) |
| `ENABLE_GROQ` | Backend | Server | Config | **YES** | `true` |
| `GROQ_BASE_URL` | Backend | Server | URL | Optional | `https://api.groq.com/openai/v1` (defaults automatically) |
| `GROQ_DEFAULT_MODEL` | Backend | Server | Config | Optional | `llama-3.3-70b-versatile` |
| `OPENAI_API_KEY` | Backend | Server | Secret | Optional | Optional OpenAI fallback |
| `GEMINI_API_KEY` | Backend | Server | Secret | Optional | Optional Gemini fallback |
| `TAVILY_API_KEY` | Backend | Server | Secret | Optional | Optional Tavily Web Research |
| `REDIS_URL` | Backend | Server | Secret | Optional | Redis Cache / Rate Limiter (in-memory fallback when absent) |
| `RATE_LIMIT_ENABLED` | Backend | Server | Config | Optional | `true` (defaults to true) |
| `CLERK_JWT_TEST_SECRET` | Backend | Server | Secret | **FORBIDDEN** | Must NOT be set in production (test mode only) |
