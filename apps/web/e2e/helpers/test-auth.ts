import { BrowserContext, Page } from "@playwright/test";

/**
 * ==============================================================================
 * IdeaGPT Playwright E2E Deterministic Test Authentication Fixture
 * ==============================================================================
 *
 * HOW IT WORKS:
 * 1. Playwright browser context injects a secure session cookie (`ideagpt_test_session`)
 *    and local storage token (`ideagpt_test_token`).
 * 2. Next.js middleware in `proxy.ts` verifies `process.env.NODE_ENV !== "production"`
 *    and permits the test session to access protected dashboard routes.
 * 3. `useApiClient` in `apps/web/lib/api/client.ts` attaches the test token to all
 *    authenticated backend requests via `Authorization: Bearer <token>`.
 *
 * WHY IT IS PRODUCTION-SAFE:
 * - Guarded strictly by `process.env.NODE_ENV !== "production"`. In production builds,
 *   Next.js compiles `NODE_ENV === "production"`, rendering the test bypass code dead.
 * - Real production Clerk keys and RS256 JWKS verification are completely untouched.
 * - No production secrets or live Clerk API keys are leaked or hardcoded.
 *
 * TENANT OWNERSHIP MAPPING:
 * - User A: `sub: user_tenant_a_101`, `tenant_id: 101`, `org: Tenant Alpha`
 * - User B: `sub: user_tenant_b_202`, `tenant_id: 202`, `org: Tenant Beta`
 * ==============================================================================
 */

export interface TestUser {
  id: string;
  email: string;
  name: string;
  token: string;
  tenantId: number;
}

export const TEST_USER_A: TestUser = {
  id: "user_tenant_a_101",
  email: "founder.a@ideagpt-test.local",
  name: "Alice Founder",
  token: "test-auth-token-tenant-a",
  tenantId: 101,
};

export const TEST_USER_B: TestUser = {
  id: "user_tenant_b_202",
  email: "founder.b@ideagpt-test.local",
  name: "Bob Competitor",
  token: "test-auth-token-tenant-b",
  tenantId: 202,
};

/**
 * Sets up an authenticated test session on the Playwright BrowserContext and Page.
 */
export async function authenticateAsTestUser(
  context: BrowserContext,
  page: Page,
  user: TestUser = TEST_USER_A
): Promise<void> {
  // 1. Set test session and token cookies for Next.js middleware, DashboardLayout, and client
  await context.addCookies([
    {
      name: "ideagpt_test_session",
      value: user.id,
      url: "http://localhost:3000",
    },
    {
      name: "ideagpt_test_token",
      value: user.id,
      url: "http://localhost:3000",
    },
  ]);

  // 2. Inject localStorage token before page scripts execute
  await page.addInitScript((userData) => {
    window.localStorage.setItem("ideagpt_test_token", userData.id);
    window.localStorage.setItem("ideagpt_test_user_id", userData.id);
  }, user);
}
