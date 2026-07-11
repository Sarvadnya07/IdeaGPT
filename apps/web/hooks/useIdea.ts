import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { useAuth } from "@clerk/nextjs";

export interface IdeaData {
  id?: number;
  project_id: number;
  elevator_pitch: string;
  target_audience: string;
  core_problem: string;
  existing_tech_stack?: string;
  primary_platforms?: string;
  monetization_model?: string;
  key_competitors?: string;
  technical_risks?: string;
  created_at?: string;
  updated_at?: string;
}

export const useIdea = (projectId?: number) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const getHeaders = async () => {
    const token = await getToken();
    return { Authorization: `Bearer ${token}` };
  };

  const ideaQuery = useQuery({
    queryKey: ["idea", projectId],
    queryFn: async () => {
      if (!projectId) return null;
      const headers = await getHeaders();
      const res = await api.get<IdeaData>(`/projects/${projectId}/idea`, { headers });
      return res.data;
    },
    enabled: !!projectId,
  });

  const saveIdea = useMutation({
    mutationFn: async ({ projectId, payload }: { projectId: number; payload: Partial<IdeaData> }) => {
      const headers = await getHeaders();
      const res = await api.post<IdeaData>(`/projects/${projectId}/idea`, payload, { headers });
      return res.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["idea", variables.projectId] });
    },
  });

  return {
    ideaQuery,
    saveIdea,
  };
};
