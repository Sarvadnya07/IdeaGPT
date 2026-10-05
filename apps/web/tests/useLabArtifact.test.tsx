import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useLabArtifact } from "../hooks/useLabArtifact";

const mockGet = vi.fn();

vi.mock("@/lib/api/client", () => ({
  useApiClient: () => ({
    get: mockGet,
  }),
}));

describe("useLabArtifact Hook (V1.1-MUST-01)", () => {
  it("fetches the latest artifact and exposes rehydrated payload", async () => {
    mockGet.mockResolvedValueOnce({
      data: [
        {
          id: "artifact-investor-01",
          artifact_type: "investor_lab",
          project_id: "proj-123",
          title: "Investor Analysis",
          created_at: "2026-09-01T12:00:00Z",
          content_payload: {
            valuation_range: { pre_money_min_usd: 1000000 },
            elevator_pitch: "AI for high-growth tech",
          },
        },
      ],
    });

    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(
      () => useLabArtifact("proj-123", "investor_lab"),
      { wrapper }
    );

    expect(result.current.isLoading).toBe(true);
    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockGet).toHaveBeenCalledWith("/ai/artifacts", {
      params: {
        project_id: "proj-123",
        artifact_type: "investor_lab",
        limit: 1,
      },
    });
    expect(result.current.isRestored).toBe(true);
    expect(result.current.artifact?.id).toBe("artifact-investor-01");
    expect(result.current.payload).toEqual({
      valuation_range: { pre_money_min_usd: 1000000 },
      elevator_pitch: "AI for high-growth tech",
    });
  });

  it("does not fetch when projectId is null/undefined", async () => {
    mockGet.mockClear();
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(
      () => useLabArtifact(null, "github_lab"),
      { wrapper }
    );

    expect(result.current.isRestored).toBe(false);
    expect(result.current.payload).toBeNull();
    expect(mockGet).not.toHaveBeenCalled();
  });
});
