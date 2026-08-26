import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export const useEvaluationPolling = (jobId: string | null) => {
  const api = useApiClient();
  const queryClient = useQueryClient();

  const statusQuery = useQuery({
    queryKey: ["evaluationStatus", jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const res = await api.get(`/evaluations/${jobId}`);
      return res.data;
    },
    enabled: !!jobId,
    // Poll every 3 seconds if status is active (PENDING, RUNNING, or QUEUED)
    refetchInterval: (query) => {
      const data = query.state.data as any;
      if (data && (["PENDING", "RUNNING", "QUEUED", "queued", "processing"].includes(data.status))) {
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
