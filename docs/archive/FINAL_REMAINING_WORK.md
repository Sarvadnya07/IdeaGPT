# IdeaGPT — Final Remaining Work & External Configuration

## In-Repository Codebase Status: 100% COMPLETE & VERIFIED

All codebase defects, type errors, schema alignments, security guards, rate limits, FinOps guardrails, and automated tests have been fully implemented and verified.

## External Production Configuration Required (Pre-Launch Ops)

The following operational tasks require external cloud platform configuration prior to production traffic:

1. **Clerk Production Instance**:
   - Create production application in Clerk Dashboard.
   - Configure custom domain (e.g. `https://clerk.ideagpt.com`).
   - Set `CLERK_PUBLISHABLE_KEY=pk_live_...` and `CLERK_JWT_ISSUER=https://clerk.ideagpt.com` in production environment.
   - Customize Clerk session token to include `{{ user.primary_email_address }}` and `{{ user.full_name }}`.

2. **Production Managed PostgreSQL**:
   - Provision high-availability PostgreSQL 15+ cluster (e.g., Supabase, Neon, AWS RDS Aurora).
   - Configure connection pooling and point-in-time recovery (PITR) backups.
   - Set `DATABASE_URL=postgresql+asyncpg://...` in production API environment.
   - Run `python -m alembic upgrade head` on production deployment.

3. **Production Redis Cache**:
   - Provision production Redis cluster (e.g., Upstash, AWS ElastiCache).
   - Set `REDIS_URL=rediss://...` for distributed rate limiting and task state.

4. **Production AI Provider Credentials**:
   - Configure production Groq API key (`GROQ_API_KEY=gsk_...`).
   - Optionally configure Gemini API key (`GEMINI_API_KEY=AIza...`) and Tavily API key (`TAVILY_API_KEY=tvly-...`).
