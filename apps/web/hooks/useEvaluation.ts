import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface Evaluation {
  id: string;
  project_id: string;
  idea_id: string;
  provider?: string;
  model?: string;
  evaluation_type: string;
  status:
    | "PENDING"
    | "QUEUED"
    | "RUNNING"
    | "COMPLETED"
    | "FAILED"
    | "CANCELLED"
    | "EXPIRED";
  progress:
    | "QUEUED"
    | "INITIALIZING"
    | "GENERATING"
    | "PARSING"
    | "SAVING"
    | "COMPLETED"
    | "FAILED"
    | "CANCELLED";
  started_at?: string;
  completed_at?: string;
  duration_ms?: number;
  token_usage?: number;
  estimated_cost?: number;
  error_message?: string;
  result_payload: any;
  created_at: string;
  updated_at: string;
}

export const useEvaluation = (evaluationId?: string | null) => {
  const api = useApiClient();
  const queryClient = useQueryClient();

  const triggerEvaluation = useMutation({
    mutationFn: async ({
      ideaId,
      evaluationType,
      provider,
      model,
    }: {
      ideaId: string;
      evaluationType?: string;
      provider?: string;
      model?: string;
    }) => {
      const res = await api.post<Evaluation>(`/ideas/${ideaId}/evaluations`, {
        evaluation_type: evaluationType || "startup_evaluation",
        provider: provider || "groq",
        model: model || "llama-3.3-70b-versatile",
      });
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({
        queryKey: ["evaluations", data.idea_id],
      });
    },
  });

  const evaluationQuery = useQuery({
    queryKey: ["evaluation", evaluationId],
    queryFn: async () => {
      if (!evaluationId) return null;
      const res = await api.get<Evaluation>(`/evaluations/${evaluationId}`);
      return res.data;
    },
    enabled: !!evaluationId,
    // Poll every 2 seconds if status is queued/running
    refetchInterval: (query) => {
      const data = query.state.data;
      if (
        data &&
        (data.status === "PENDING" ||
          data.status === "QUEUED" ||
          data.status === "RUNNING")
      ) {
        return 2000;
      }
      return false;
    },
  });

  const retryEvaluation = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post<Evaluation>(`/evaluations/${id}/retry`, {});
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["evaluation", data.id] });
      queryClient.invalidateQueries({
        queryKey: ["evaluations", data.idea_id],
      });
    },
  });

  const cancelEvaluation = useMutation({
    mutationFn: async (id: string) => {
      const res = await api.post<Evaluation>(`/evaluations/${id}/cancel`, {});
      return res.data;
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["evaluation", data.id] });
      queryClient.invalidateQueries({
        queryKey: ["evaluations", data.idea_id],
      });
    },
  });

  const deleteEvaluation = useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/evaluations/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["evaluations"] });
    },
  });

  return {
    triggerEvaluation,
    evaluationQuery,
    retryEvaluation,
    cancelEvaluation,
    deleteEvaluation,
  };
};

export const useIdeaEvaluations = (ideaId?: string | null) => {
  const api = useApiClient();

  return useQuery({
    queryKey: ["evaluations", ideaId],
    queryFn: async () => {
      if (!ideaId) return [];
      const res = await api.get<Evaluation[]>(`/ideas/${ideaId}/evaluations`);
      return res.data;
    },
    enabled: !!ideaId,
  });
};
