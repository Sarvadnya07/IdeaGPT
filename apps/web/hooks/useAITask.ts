import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface AITaskData {
  id: string;
  user_id: number;
  task_type: string;
  provider: string;
  model: string;
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED" | "CANCELLED";
  attempt: number;
  result_payload?: any;
  error_message?: string;
  duration_ms?: number;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
}

export function useAITask(taskId: string | null) {
  const api = useApiClient();

  const taskQuery = useQuery<AITaskData>({
    queryKey: ["ai-task", taskId],
    queryFn: async () => {
      if (!taskId) throw new Error("No task ID");
      const res = await api.get<AITaskData>(`/ai/tasks/${taskId}`);
      return res.data;
    },
    enabled: !!taskId,
    // Safeguard #8: Poll every 2000ms, automatically stop when terminal state reached
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "COMPLETED" || status === "FAILED" || status === "CANCELLED") {
        return false;
      }
      return 2000;
    },
  });

  return {
    task: taskQuery.data,
    isLoading: taskQuery.isLoading,
    isError: taskQuery.isError,
    status: taskQuery.data?.status || null,
  };
}

export function useCreateAITask() {
  const api = useApiClient();

  return useMutation({
    mutationFn: async (payload: {
      provider?: string;
      model?: string;
      idea_id?: string;
      project_id?: string;
      input_payload?: Record<string, any>;
      idempotency_key?: string;
    }) => {
      const res = await api.post<{ id: string; status: string }>("/ai/tasks", payload);
      return res.data;
    },
  });
}
