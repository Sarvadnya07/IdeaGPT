import { describe, it, expect } from "vitest";
import { api as publicApi } from "../lib/api/index";

describe("API Client Configuration", () => {
  it("uses the correct canonical base URL with /api/v1 prefix", () => {
    expect(publicApi.defaults.baseURL).toContain("/api/v1");
  });

  it("sets standard Content-Type application/json header", () => {
    expect(publicApi.defaults.headers["Content-Type"]).toBe("application/json");
  });
});
