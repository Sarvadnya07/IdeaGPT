import { useEffect, useState, useCallback, useRef } from "react";
import { useAuth } from "@clerk/nextjs";
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
      if (
        status === "COMPLETED" ||
        status === "FAILED" ||
        status === "CANCELLED"
      ) {
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

export function useAITaskStream(taskId: string | null) {
  const { getToken } = useAuth();
  const [task, setTask] = useState<AITaskData | null>(null);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const startStream = useCallback(async () => {
    if (!taskId) return;
    setIsStreaming(true);
    setError(null);

    const controller = new AbortController();
    abortControllerRef.current = controller;

    try {
      const token = await getToken();
      const baseUrl =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
      const response = await fetch(`${baseUrl}/ai/tasks/${taskId}/stream`, {
        headers: {
          Authorization: token ? `Bearer ${token}` : "",
          Accept: "text/event-stream",
        },
        signal: controller.signal,
      });

      if (!response.ok) {
        throw new Error(`Stream connection failed: ${response.statusText}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No readable stream body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const block of lines) {
          if (!block.trim()) continue;
          const eventMatch = block.match(/^event:\s*(\w+)/m);
          const dataMatch = block.match(/^data:\s*(.+)$/m);
          const eventType = eventMatch ? eventMatch[1] : "message";
          const dataStr = dataMatch ? dataMatch[1] : "";

          if (eventType === "task_update" && dataStr) {
            try {
              const parsed = JSON.parse(dataStr);
              setTask((prev) => ({ ...prev, ...parsed }));
            } catch (e) {
              console.error("Failed to parse SSE task update", e);
            }
          } else if (eventType === "done") {
            setIsStreaming(false);
            return;
          } else if (eventType === "error") {
            setError(dataStr || "Stream error");
            setIsStreaming(false);
            return;
          }
        }
      }
    } catch (err: any) {
      if (err.name !== "AbortError") {
        setError(err.message || "Streaming error occurred");
      }
    } finally {
      setIsStreaming(false);
    }
  }, [taskId, getToken]);

  useEffect(() => {
    if (taskId) {
      startStream();
    }
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [taskId, startStream]);

  return {
    task,
    isStreaming,
    error,
    restartStream: startStream,
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
      const res = await api.post<{ id: string; status: string }>(
        "/ai/tasks",
        payload,
      );
      return res.data;
    },
  });
}
