import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../lib/api";
import { useAuth } from "@clerk/nextjs";

export interface IdeaData {
  id?: string;
  project_id: string;
  title: string;
  problem_statement: string;
  solution_description: string;
  target_users?: string;
  industry?: string;
  business_model?: string;
  stage?: string;
  tags?: string;
  notes?: string;
  is_draft?: boolean;
  created_at?: string;
  updated_at?: string;

  // Custom analysis-only fields
  elevator_pitch?: string;
  target_audience?: string;
  core_problem?: string;
  existing_tech_stack?: string;
  primary_platforms?: string;
  monetization_model?: string;
  key_competitors?: string;
  technical_risks?: string;
}

export const useIdea = (projectId?: string | null) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const getHeaders = async () => {
    const token = await getToken();
    return { Authorization: `Bearer ${token}` };
  };

  const ideasQuery = useQuery({
    queryKey: ["ideas", projectId],
    queryFn: async () => {
      if (!projectId) return [];
      const headers = await getHeaders();
      const res = await api.get<IdeaData[]>(`/projects/${projectId}/ideas`, { headers });
      return res.data;
    },
    enabled: !!projectId,
  });

  const saveIdea = useMutation({
    mutationFn: async ({ projectId, payload }: { projectId: string; payload: Partial<IdeaData> }) => {
      const headers = await getHeaders();
      const res = await api.post<IdeaData>(`/projects/${projectId}/ideas`, payload, { headers });
      return res.data;
    },
    onSuccess: (data, variables) => {
      queryClient.invalidateQueries({ queryKey: ["ideas", variables.projectId] });
    },
  });

  return {
    ideasQuery,
    saveIdea,
  };
};
