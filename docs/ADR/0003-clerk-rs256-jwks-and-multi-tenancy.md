# 3. Clerk RS256 JWKS Key Verification & Multi-Tenant Scoping

Date: 2026-08-16

## Status

Accepted

## Context

IdeaGPT processes proprietary intellectual property and startup concepts. We required robust authentication without storing user passwords locally, zero secret leakage to client bundles, and strict multi-tenant data isolation.

## Decision

1. **Cryptographic JWT Verification**: Enforce RS256 JWKS public key verification using `PyJWKClient` with a 5-minute key cache. Reject unverified decoding, algorithm confusion (`HS256`/`none` in production), and missing `sub`.
2. **Deterministic Test Mode Isolation**: Dedicated HS256 test path activated only when `APP_ENV=test` AND `CLERK_JWT_TEST_SECRET` are both explicitly set.
3. **Multi-Tenant Row-Level Scoping**: Enforce user ownership scoping at the ORM layer (`Project.user_id == current_user.id`) across all domain services and database queries.
4. **User Auto-Synchronization**: Synchronize Clerk user IDs into PostgreSQL upon first authenticated request within an ACID retry loop.

## Consequences

### Pros:

- Zero local password or sensitive credential storage.
- High authentication performance due to JWKS key caching.
- Guaranteed multi-tenant data isolation preventing horizontal privilege escalation.
- Zero secret leakage in frontend bundles.

### Cons:

- Initial startup requires network connectivity to Clerk's JWKS endpoint (or cached keys).
