import { describe, it, expect } from "vitest";

import { normalizeApiError } from "../lib/api/errors";

function axiosError(status: number, data?: unknown) {
  return { response: { status, data } };
}

describe("normalizeApiError", () => {
  it("maps 401 to a re-authenticate message", () => {
    expect(normalizeApiError(axiosError(401)).message).toContain("sign in again");
  });

  it("maps 403 to an access-denied message, not a re-auth prompt", () => {
    // PRODUCT-01 P-12: re-authenticating cannot fix an authorization denial.
    const result = normalizeApiError(axiosError(403));
    expect(result.message).toContain("do not have access");
    expect(result.message).not.toContain("sign in again");
  });

  it("prefers the server detail on 403 when the API explains the denial", () => {
    const result = normalizeApiError(
      axiosError(403, { detail: "One or more selected evaluations do not exist or access is denied." }),
    );
    expect(result.message).toBe(
      "One or more selected evaluations do not exist or access is denied.",
    );
  });

  it("prefers the server detail string when provided", () => {
    const result = normalizeApiError(
      axiosError(422, { detail: "title: String should have at most 100 characters" }),
    );
    expect(result.message).toBe("title: String should have at most 100 characters");
  });

  it("joins array-shaped validation details into one message", () => {
    const result = normalizeApiError(
      axiosError(422, { detail: [{ msg: "field a invalid" }, { msg: "field b invalid" }] }),
    );
    expect(result.message).toBe("field a invalid, field b invalid");
  });

  it("falls back to a generic message for 429 without server detail", () => {
    expect(normalizeApiError(axiosError(429)).message).toContain("Rate limit");
  });

  it("falls back to a generic message for 5xx without server detail", () => {
    expect(normalizeApiError(axiosError(503)).message).toContain("Internal Server Error");
  });

  it("reports a network error when no response was received", () => {
    const result = normalizeApiError(new Error("Network Error"));
    expect(result.isNetworkError).toBe(true);
    expect(result.status).toBeUndefined();
    expect(result.message).toContain("Cannot connect to API server");
  });

  it("handles an unexpected response shape without throwing", () => {
    const result = normalizeApiError(axiosError(418, undefined));
    expect(result.status).toBe(418);
    expect(result.isNetworkError).toBe(false);
  });

  it("never throws on non-object input", () => {
    expect(() => normalizeApiError(null)).not.toThrow();
    expect(() => normalizeApiError("boom")).not.toThrow();
    expect(() => normalizeApiError(undefined)).not.toThrow();
  });
});
