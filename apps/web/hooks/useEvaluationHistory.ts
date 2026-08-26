import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export function useEvaluationHistory(ideaId: string | null) {
  const api = useApiClient();

  return useQuery({
    queryKey: ["evaluation-history", ideaId],
    queryFn: async () => {
      const res = await api.get(`/ideas/${ideaId}/evaluations`);
      return res.data as Array<{
        id: string;
        status: string;
        score?: number;
        created_at: string;
        completed_at?: string;
        provider?: string;
        model?: string;
        evaluation_type?: string;
        duration_ms?: number;
      }>;
    },
    enabled: !!ideaId,
    staleTime: 30 * 1000,
  });
}
