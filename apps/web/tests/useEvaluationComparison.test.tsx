import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import {
  useEvaluationComparison,
  EvaluationVersionComparisonResponse,
} from "../hooks/useEvaluationComparison";
import { EvaluationComparisonView } from "../components/evaluation/EvaluationComparisonView";

const mockGet = vi.fn();

vi.mock("@/lib/api/client", () => ({
  useApiClient: () => ({
    get: mockGet,
  }),
}));

describe("useEvaluationComparison Hook (Stage 4A)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("does not execute query if parameters are missing or identical", () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    // Missing A and B
    const { result: r1 } = renderHook(() => useEvaluationComparison("idea-1", null, null), { wrapper });
    expect(r1.current.isLoading).toBe(false);
    expect(mockGet).not.toHaveBeenCalled();

    // A === B
    const { result: r2 } = renderHook(() => useEvaluationComparison("idea-1", "eval-1", "eval-1"), { wrapper });
    expect(r2.current.isLoading).toBe(false);
    expect(mockGet).not.toHaveBeenCalled();
  });

  it("executes query and returns comparison data when two distinct runs are provided", async () => {
    const mockData: EvaluationVersionComparisonResponse = {
      idea_id: "idea-101",
      evaluation_a: {
        id: "eval-v1",
        created_at: "2026-01-01T10:00:00Z",
        completed_at: "2026-01-01T10:01:00Z",
        status: "COMPLETED",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 1200,
        token_usage: 1500,
        estimated_cost: 0.002,
        score: 70.0,
      },
      evaluation_b: {
        id: "eval-v2",
        created_at: "2026-01-02T10:00:00Z",
        completed_at: "2026-01-02T10:01:00Z",
        status: "COMPLETED",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 950,
        token_usage: 1600,
        estimated_cost: 0.0025,
        score: 85.0,
      },
      overall_score: {
        key: "overall_score",
        label: "Overall Readiness Score",
        value_a: 70.0,
        value_b: 85.0,
        delta: 15.0,
        formatted_delta: "+15.00",
        status: "improved",
        direction: "higher_is_better",
      },
      dimensions: [
        {
          key: "innovation",
          label: "Innovation",
          value_a: 65.0,
          value_b: 80.0,
          delta: 15.0,
          formatted_delta: "+15.00",
          status: "improved",
          direction: "higher_is_better",
        },
        {
          key: "execution_complexity",
          label: "Execution Complexity",
          value_a: 80.0,
          value_b: 60.0,
          delta: -20.0,
          formatted_delta: "-20.00",
          status: "improved", // lower complexity is improved!
          direction: "lower_is_better",
        },
      ],
      swot: {
        strengths: {
          added: ["Proprietary AI dataset"],
          removed: [],
          retained: ["Strong founder pedigree"],
        },
        weaknesses: {
          added: [],
          removed: ["Unclear pricing model"],
          retained: [],
        },
      },
      sections: [
        {
          section_key: "architecture_breakdown",
          label: "Technical Architecture",
          present_in_a: true,
          present_in_b: true,
          status: "changed",
          diff_summary: "Updated to distributed cache architecture",
        },
      ],
      provenance_comparison: {
        provider_transition: "groq -> groq",
        model_transition: "llama-3.3-70b-versatile -> llama-3.3-70b-versatile",
        duration_ms_delta: -250,
        token_usage_delta: 100,
        estimated_cost_delta: 0.0005,
      },
      summary: "Overall score changed by +15.00 points (70.00 -> 85.00, Improved).",
      generated_at: "2026-01-02T10:05:00Z",
    };

    mockGet.mockResolvedValueOnce({ data: mockData });

    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(
      () => useEvaluationComparison("idea-101", "eval-v1", "eval-v2"),
      { wrapper }
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(mockGet).toHaveBeenCalledWith("/evaluations/idea-101/compare?a=eval-v1&b=eval-v2");
    expect(result.current.data?.overall_score.formatted_delta).toBe("+15.00");
    expect(result.current.data?.overall_score.status).toBe("improved");
  });
});

describe("EvaluationComparisonView Component (Stage 4A)", () => {
  const dummyRuns = [
    {
      id: "run-1",
      status: "COMPLETED",
      created_at: "2026-01-01T10:00:00Z",
      score: 70,
      provider: "groq",
      model: "llama-3.3-70b-versatile",
    },
    {
      id: "run-2",
      status: "COMPLETED",
      created_at: "2026-01-02T10:00:00Z",
      score: 85,
      provider: "groq",
      model: "llama-3.3-70b-versatile",
    },
  ];

  it("renders empty state when selectors are not populated", () => {
    render(
      <EvaluationComparisonView
        runs={dummyRuns}
        selectedA={null}
        selectedB={null}
        onSelectA={vi.fn()}
        onSelectB={vi.fn()}
        comparison={null}
        isLoading={false}
        isError={false}
      />
    );

    expect(screen.getByText(/Select Two Evaluation Runs/i)).toBeDefined();
    expect(screen.getByTestId("selector-evaluation-a")).toBeDefined();
    expect(screen.getByTestId("selector-evaluation-b")).toBeDefined();
  });

  it("renders loading state during calculation", () => {
    render(
      <EvaluationComparisonView
        runs={dummyRuns}
        selectedA="run-1"
        selectedB="run-2"
        onSelectA={vi.fn()}
        onSelectB={vi.fn()}
        comparison={null}
        isLoading={true}
        isError={false}
      />
    );

    expect(screen.getByText(/Calculating deterministic version comparison/i)).toBeDefined();
  });

  it("renders comparison results with accessible semantic badges", () => {
    const mockComparison: EvaluationVersionComparisonResponse = {
      idea_id: "idea-101",
      evaluation_a: {
        id: "run-1",
        created_at: "2026-01-01T10:00:00Z",
        completed_at: "2026-01-01T10:01:00Z",
        status: "COMPLETED",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 1200,
        token_usage: 1500,
        estimated_cost: 0.002,
        score: 70,
      },
      evaluation_b: {
        id: "run-2",
        created_at: "2026-01-02T10:00:00Z",
        completed_at: "2026-01-02T10:01:00Z",
        status: "COMPLETED",
        provider: "groq",
        model: "llama-3.3-70b-versatile",
        duration_ms: 950,
        token_usage: 1600,
        estimated_cost: 0.0025,
        score: 85,
      },
      overall_score: {
        key: "overall_score",
        label: "Overall Readiness Score",
        value_a: 70,
        value_b: 85,
        delta: 15,
        formatted_delta: "+15.00",
        status: "improved",
        direction: "higher_is_better",
      },
      dimensions: [
        {
          key: "innovation",
          label: "Innovation",
          value_a: 65,
          value_b: 80,
          delta: 15,
          formatted_delta: "+15.00",
          status: "improved",
          direction: "higher_is_better",
        },
      ],
      swot: {
        strengths: {
          added: ["Proprietary Dataset"],
          removed: [],
          retained: ["Strong Team"],
        },
        weaknesses: {
          added: [],
          removed: ["High Burn Rate"],
          retained: [],
        },
      },
      sections: [
        {
          section_key: "architecture_breakdown",
          label: "Technical Architecture",
          present_in_a: true,
          present_in_b: true,
          status: "changed",
          diff_summary: "Upgraded database cluster",
        },
      ],
      provenance_comparison: {
        provider_transition: "groq -> groq",
        model_transition: "llama-3.3-70b-versatile -> llama-3.3-70b-versatile",
        duration_ms_delta: -250,
        token_usage_delta: 100,
        estimated_cost_delta: 0.0005,
      },
      summary: "Overall score changed by +15.00 points (70.00 -> 85.00, Improved).",
      generated_at: "2026-01-02T10:05:00Z",
    };

    render(
      <EvaluationComparisonView
        runs={dummyRuns}
        selectedA="run-1"
        selectedB="run-2"
        onSelectA={vi.fn()}
        onSelectB={vi.fn()}
        comparison={mockComparison}
        isLoading={false}
        isError={false}
      />
    );

    // Accessible text badge checks
    expect(screen.getByTestId("overall-delta-value").textContent).toBe("+15.00");
    expect(screen.getByTestId("overall-delta-badge").textContent).toBe("[Improved]");
    expect(screen.getByText("Proprietary Dataset", { exact: false })).toBeDefined();
    expect(screen.getByText("RESOLVED", { exact: true })).toBeDefined();
    expect(screen.getByText("High Burn Rate", { exact: false })).toBeDefined();
    expect(screen.getByText("Technical Architecture", { exact: false })).toBeDefined();
    expect(screen.getByText("Upgraded database cluster", { exact: false })).toBeDefined();
  });
});
