/**
 * Development-only test-token bridge.
 *
 * Lets local development and E2E tooling inject a bearer token without a real
 * Clerk session. This previously lived inline inside the Axios request
 * interceptor, where it was easy to miss and hard to test.
 *
 * Hard guarantees:
 *   - Disabled whenever NODE_ENV === "production" (checked on every read, not
 *     just at module load, so it cannot be enabled by a build-time mistake).
 *   - Returns null outside the browser, so SSR never touches localStorage.
 *   - Never throws: storage/cookie access can fail under strict privacy modes.
 */

export const DEV_TEST_TOKEN_STORAGE_KEY = "ideagpt_test_token";
export const DEV_TEST_TOKEN_COOKIE_KEYS = [
  "ideagpt_test_token",
  "ideagpt_test_session",
] as const;

/** True only in non-production browser environments. */
export function isDevTestTokenBridgeEnabled(): boolean {
  return process.env.NODE_ENV !== "production" && typeof window !== "undefined";
}

function readCookieValue(tokenKey: string): string | null {
  const match = document.cookie
    .split("; ")
    .find((row) => row.startsWith(`${tokenKey}=`));
  return match ? match.split("=")[1] || null : null;
}

/**
 * Resolve a development test token, or null when unavailable/disabled.
 * Prefers localStorage, then falls back to the well-known test cookies.
 */
export function readDevTestToken(): string | null {
  if (!isDevTestTokenBridgeEnabled()) {
    return null;
  }

  try {
    const stored = window.localStorage.getItem(DEV_TEST_TOKEN_STORAGE_KEY);
    if (stored) {
      return stored;
    }
  } catch {
    // Storage can be unavailable (private mode, blocked third-party context).
  }

  for (const cookieKey of DEV_TEST_TOKEN_COOKIE_KEYS) {
    const value = readCookieValue(cookieKey);
    if (value) {
      return value;
    }
  }

  return null;
}
