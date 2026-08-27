import { describe, it, expect, vi } from "vitest";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import { useAICredentials } from "../hooks/useAICredentials";

vi.mock("@/lib/api/client", () => ({
  useApiClient: () => ({
    get: vi.fn().mockResolvedValue({
      data: [
        {
          id: "cred-1",
          provider: "groq",
          key_hint: "gsk_...3a9f",
          status: "ACTIVE",
          configured: true,
          verified: true,
          created_at: "2026-08-27T10:00:00Z",
          updated_at: "2026-08-27T10:00:00Z",
        },
      ],
    }),
    post: vi.fn().mockResolvedValue({
      data: {
        id: "cred-2",
        provider: "openai",
        key_hint: "sk-...8b2c",
        status: "ACTIVE",
      },
    }),
    delete: vi.fn().mockResolvedValue({ data: { message: "Revoked" } }),
  }),
}));

describe("useAICredentials Hook", () => {
  it("fetches and returns configured BYOK credentials with masked hints", async () => {
    const queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(() => useAICredentials(), { wrapper });

    await waitFor(() => expect(result.current.credentials.length).toBe(1));
    expect(result.current.credentials[0].provider).toBe("groq");
    expect(result.current.credentials[0].key_hint).toBe("gsk_...3a9f");
  });
});
