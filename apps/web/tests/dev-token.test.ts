import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";

import {
  DEV_TEST_TOKEN_COOKIE_KEYS,
  DEV_TEST_TOKEN_STORAGE_KEY,
  isDevTestTokenBridgeEnabled,
  readDevTestToken,
} from "../lib/api/dev-token";

/**
 * jsdom in this workspace does not expose localStorage (opaque origin), and
 * the production code deliberately tolerates its absence. Install an in-memory
 * shim so the storage happy-path can still be asserted.
 */
function installLocalStorageShim() {
  if (typeof window === "undefined") return;
  if (window.localStorage) return;

  const store = new Map<string, string>();
  const shim: Storage = {
    get length() {
      return store.size;
    },
    clear: () => store.clear(),
    getItem: (key) => (store.has(key) ? store.get(key)! : null),
    key: (index) => Array.from(store.keys())[index] ?? null,
    removeItem: (key) => void store.delete(key),
    setItem: (key, value) => void store.set(key, String(value)),
  };

  Object.defineProperty(window, "localStorage", {
    configurable: true,
    value: shim,
  });
}

describe("dev-token bridge", () => {
  beforeEach(() => {
    installLocalStorageShim();
    window.localStorage.clear();
    // Clear every cookie the bridge reads so tests cannot leak into each other.
    for (const cookieKey of DEV_TEST_TOKEN_COOKIE_KEYS) {
      document.cookie = `${cookieKey}=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/`;
    }
  });

  afterEach(() => {
    vi.unstubAllEnvs();
    window.localStorage.clear();
  });

  it("is enabled outside production", () => {
    vi.stubEnv("NODE_ENV", "development");
    expect(isDevTestTokenBridgeEnabled()).toBe(true);
  });

  it("is disabled in production even if a token is present", () => {
    window.localStorage.setItem(DEV_TEST_TOKEN_STORAGE_KEY, "leaked-token");
    vi.stubEnv("NODE_ENV", "production");

    expect(isDevTestTokenBridgeEnabled()).toBe(false);
    expect(readDevTestToken()).toBeNull();
  });

  it("reads a token from localStorage when enabled", () => {
    vi.stubEnv("NODE_ENV", "development");
    window.localStorage.setItem(DEV_TEST_TOKEN_STORAGE_KEY, "local-token");
    expect(readDevTestToken()).toBe("local-token");
  });

  it("falls back to the test cookie when storage is empty", () => {
    vi.stubEnv("NODE_ENV", "development");
    document.cookie = "ideagpt_test_session=cookie-token";
    expect(readDevTestToken()).toBe("cookie-token");
  });

  it("returns null when no token source is available", () => {
    vi.stubEnv("NODE_ENV", "development");
    expect(readDevTestToken()).toBeNull();
  });
});
