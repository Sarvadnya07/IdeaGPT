import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export const useEvaluationPolling = (jobId: number | null) => {
  const api = useApiClient();
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ["evaluationStatus", jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const res = await api.get(`/evaluations/${jobId}/status`);
      return res.data;
    },
    enabled: !!jobId,
    // Poll every 3 seconds if status is queued or processing
    refetchInterval: (query) => {
      const data = query.state.data as any;
      if (data && (data.status === "queued" || data.status === "processing")) {
        return 3000;
      }
      return false;
    },
  });

  const retryMutation = useMutation({
    mutationFn: async () => {
      if (!jobId) throw new Error("No job ID");
      const res = await api.post(`/evaluations/${jobId}/retry`);
      return res.data;
    },
    onSuccess: (data) => {
      // Re-initialize polling with new job ID
      queryClient.invalidateQueries({ queryKey: ["evaluationStatus"] });
    },
  });

  return {
    statusQuery,
    retryMutation,
  };
};
