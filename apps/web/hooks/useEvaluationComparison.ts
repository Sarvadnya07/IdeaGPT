import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface DimensionDelta {
  key: string;
  label: string;
  value_a: number | null;
  value_b: number | null;
  delta: number | null;
  formatted_delta: string | null;
  status: "improved" | "declined" | "unchanged" | "unavailable";
  direction: "higher_is_better" | "lower_is_better";
}

export interface ListDelta {
  added: string[];
  removed: string[];
  retained: string[];
}

export interface SectionDelta {
  section_key: string;
  label: string;
  present_in_a: boolean;
  present_in_b: boolean;
  status: "changed" | "unchanged" | "added" | "removed" | "unavailable";
  diff_summary?: string | null;
  value_a?: unknown;
  value_b?: unknown;
}

export interface EvaluationProvenance {
  id: string;
  created_at: string | null;
  completed_at: string | null;
  status: string;
  provider: string | null;
  model: string | null;
  duration_ms: number | null;
  token_usage: number | null;
  estimated_cost: number | null;
  score: number | null;
}

export interface EvaluationVersionComparisonResponse {
  idea_id: string;
  evaluation_a: EvaluationProvenance;
  evaluation_b: EvaluationProvenance;
  overall_score: DimensionDelta;
  confidence?: DimensionDelta | null;
  dimensions: DimensionDelta[];
  swot: Record<string, ListDelta>;
  sections: SectionDelta[];
  provenance_comparison: {
    provider_transition: string;
    model_transition: string;
    duration_ms_delta: number | null;
    token_usage_delta: number | null;
    estimated_cost_delta: number | null;
  };
  summary: string;
  generated_at: string;
}

export function useEvaluationComparison(
  ideaId: string | null,
  evaluationAId: string | null,
  evaluationBId: string | null
) {
  const api = useApiClient();

  const isEnabled = Boolean(
    ideaId &&
    evaluationAId &&
    evaluationBId &&
    evaluationAId !== evaluationBId
  );

  return useQuery<EvaluationVersionComparisonResponse, Error>({
    queryKey: ["evaluation-version-comparison", ideaId, evaluationAId, evaluationBId],
    queryFn: async () => {
      const res = await api.get(
        `/evaluations/${ideaId}/compare?a=${encodeURIComponent(
          evaluationAId!
        )}&b=${encodeURIComponent(evaluationBId!)}`
      );
      return res.data;
    },
    enabled: isEnabled,
    staleTime: 60 * 1000,
    retry: 1,
  });
}
