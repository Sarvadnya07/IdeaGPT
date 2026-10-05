import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface AIArtifactItem<T = Record<string, unknown>> {
  id: string;
  artifact_type: string;
  title?: string | null;
  project_id?: string | null;
  idea_id?: string | null;
  provider?: string | null;
  model?: string | null;
  execution_type?: string | null;
  fallback_used?: boolean;
  content_payload?: T | null;
  created_at?: string | null;
}

/**
 * Reusable hook to fetch and rehydrate the latest AI artifact for a lab
 * (V1.1-MUST-01: AI Lab Artifact Persistence + History Rehydration).
 */
export function useLabArtifact<T = Record<string, unknown>>(
  projectId: string | null | undefined,
  artifactType: string,
  options?: { enabled?: boolean }
) {
  const api = useApiClient();
  const queryClient = useQueryClient();

  const queryKey = ["lab-artifact", projectId, artifactType];

  const query = useQuery({
    queryKey,
    queryFn: async (): Promise<AIArtifactItem<T> | null> => {
      if (!projectId) return null;
      const res = await api.get<AIArtifactItem<T>[]>("/ai/artifacts", {
        params: {
          project_id: projectId,
          artifact_type: artifactType,
          limit: 1,
        },
      });
      if (res.data && res.data.length > 0) {
        return res.data[0];
      }
      return null;
    },
    enabled: options?.enabled !== false && !!projectId,
    staleTime: 30 * 1000,
  });

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey });
    await queryClient.invalidateQueries({
      queryKey: ["projectArtifacts", projectId],
    });
  };

  return {
    ...query,
    artifact: query.data ?? null,
    payload: (query.data?.content_payload as T | null) ?? null,
    isRestored: !query.isLoading && !!query.data?.content_payload,
    invalidate,
  };
}
