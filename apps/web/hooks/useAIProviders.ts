import { useQuery } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface AIProviderInfo {
  id: string;
  name: string;
  configured: boolean;
  enabled: boolean;
}

export interface AIModelInfo {
  id: string;
  name: string;
  provider: string;
  capabilities: string[];
  configured: boolean;
  available: boolean;
}

export function useAIProviders() {
  const api = useApiClient();

  const providersQuery = useQuery<AIProviderInfo[]>({
    queryKey: ["ai-providers"],
    queryFn: async () => {
      const res = await api.get<AIProviderInfo[]>("/ai/providers");
      return res.data;
    },
    staleTime: 60 * 1000,
  });

  const modelsQuery = useQuery<AIModelInfo[]>({
    queryKey: ["ai-models"],
    queryFn: async () => {
      const res = await api.get<AIModelInfo[]>("/ai/models");
      return res.data;
    },
    staleTime: 60 * 1000,
  });

  return {
    providers: providersQuery.data || [],
    models: modelsQuery.data || [],
    isLoading: providersQuery.isLoading || modelsQuery.isLoading,
    isError: providersQuery.isError || modelsQuery.isError,
  };
}
