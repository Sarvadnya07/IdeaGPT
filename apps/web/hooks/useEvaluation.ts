import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { useAuth } from "@clerk/nextjs";

export interface EvaluationJob {
  id: number;
  status: "QUEUED" | "PROCESSING" | "COMPLETED" | "FAILED";
  result_payload: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export const useEvaluation = (jobId?: number | null) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const getHeaders = async () => {
    const token = await getToken();
    return { Authorization: `Bearer ${token}` };
  };

  const triggerEvaluation = useMutation({
    mutationFn: async (projectId: number) => {
      const headers = await getHeaders();
      const res = await api.post<EvaluationJob>(`/projects/${projectId}/evaluate`, {}, { headers });
      return res.data;
    },
  });

  const evaluationQuery = useQuery({
    queryKey: ["evaluation", jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const headers = await getHeaders();
      const res = await api.get<EvaluationJob>(`/evaluations/${jobId}/status`, { headers });
      return res.data;
    },
    enabled: !!jobId,
    // Poll every 3 seconds if status is QUEUED or PROCESSING
    refetchInterval: (query) => {
      const data = query.state.data;
      if (data && (data.status === "QUEUED" || data.status === "PROCESSING")) {
        return 3000;
      }
      return false;
    },
  });

  return {
    triggerEvaluation,
    evaluationQuery,
  };
};
