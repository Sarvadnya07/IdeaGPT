import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
});

export const useEvaluationPolling = (jobId: number | null) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const getHeaders = async () => {
    const token = await getToken();
    return { Authorization: `Bearer ${token}` };
  };

  const statusQuery = useQuery({
    queryKey: ["evaluationStatus", jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const headers = await getHeaders();
      const res = await api.get(`/evaluations/${jobId}/status`, { headers });
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
      const headers = await getHeaders();
      const res = await api.post(`/evaluations/${jobId}/retry`, {}, { headers });
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
