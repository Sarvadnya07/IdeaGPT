import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

export interface AICredentialInfo {
  id: string;
  provider: string;
  key_hint: string;
  status: string;
  configured: boolean;
  verified: boolean;
  last_verified_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CredentialVerifyResult {
  provider: string;
  valid: boolean;
  status: string;
  message: string;
  latency_ms: number;
}

export function useAICredentials() {
  const api = useApiClient();
  const queryClient = useQueryClient();

  const credentialsQuery = useQuery<AICredentialInfo[]>({
    queryKey: ["ai-credentials"],
    queryFn: async () => {
      const res = await api.get<AICredentialInfo[]>("/ai/credentials");
      return res.data;
    },
  });

  const saveCredentialMutation = useMutation({
    mutationFn: async ({
      provider,
      apiKey,
    }: {
      provider: string;
      apiKey: string;
    }) => {
      const res = await api.post<AICredentialInfo>("/ai/credentials", {
        provider,
        api_key: apiKey,
      });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-credentials"] });
      queryClient.invalidateQueries({ queryKey: ["ai-providers"] });
    },
  });

  const verifyCredentialMutation = useMutation({
    mutationFn: async (provider: string) => {
      const res = await api.post<CredentialVerifyResult>(
        `/ai/credentials/${provider}/verify`,
      );
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-credentials"] });
    },
  });

  const deleteCredentialMutation = useMutation({
    mutationFn: async (provider: string) => {
      const res = await api.delete(`/ai/credentials/${provider}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-credentials"] });
      queryClient.invalidateQueries({ queryKey: ["ai-providers"] });
    },
  });

  return {
    credentials: credentialsQuery.data || [],
    isLoading: credentialsQuery.isLoading,
    saveCredential: saveCredentialMutation.mutateAsync,
    isSaving: saveCredentialMutation.isPending,
    verifyCredential: verifyCredentialMutation.mutateAsync,
    isVerifying: verifyCredentialMutation.isPending,
    deleteCredential: deleteCredentialMutation.mutateAsync,
    isDeleting: deleteCredentialMutation.isPending,
    refetchCredentials: credentialsQuery.refetch,
  };
}
