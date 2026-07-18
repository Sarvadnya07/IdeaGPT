import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
});

export interface IdeaData {
  id?: string;
  title?: string;
  problem_statement: string;
  solution_description: string;
  target_users?: string;
  industry?: string;
  business_model?: string;
  stage?: string;
  tags?: string;
  notes?: string;
  is_draft?: boolean;

  // Custom form-only fields
  target_audience?: string;
  competitors?: string;
  unique_selling_proposition?: string;
  technology_stack?: string;
  budget?: string;
  timeline?: string;
  additional_notes?: string;

  // Custom analysis-only fields
  elevator_pitch?: string;
  core_problem?: string;
  existing_tech_stack?: string;
  primary_platforms?: string;
  monetization_model?: string;
  key_competitors?: string;
  technical_risks?: string;
}

export const useIdeaSubmission = (projectId: string | null, ideaId: string | null = null) => {
  const { getToken } = useAuth();
  const queryClient = useQueryClient();

  const getHeaders = async () => {
    const token = await getToken();
    return { Authorization: `Bearer ${token}` };
  };

  const ideaQuery = useQuery({
    queryKey: ["idea", ideaId],
    queryFn: async () => {
      if (!ideaId) return null;
      const headers = await getHeaders();
      const res = await api.get<IdeaData>(`/ideas/${ideaId}`, { headers });
      return res.data;
    },
    enabled: !!ideaId,
  });

  const ideasListQuery = useQuery({
    queryKey: ["ideas", projectId],
    queryFn: async () => {
      if (!projectId) return [];
      const headers = await getHeaders();
      const res = await api.get<IdeaData[]>(`/projects/${projectId}/ideas`, { headers });
      return res.data;
    },
    enabled: !!projectId,
  });

  const saveIdeaMutation = useMutation({
    mutationFn: async (data: Partial<IdeaData>) => {
      const headers = await getHeaders();
      if (ideaId) {
        // Update existing
        const res = await api.patch<IdeaData>(`/ideas/${ideaId}`, data, { headers });
        return res.data;
      } else {
        // Create new
        if (!projectId) throw new Error("No project ID for new idea creation");
        const res = await api.post<IdeaData>(`/projects/${projectId}/ideas`, data, { headers });
        return res.data;
      }
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["idea", ideaId] });
      queryClient.invalidateQueries({ queryKey: ["ideas", projectId] });
    },
  });

  const triggerEvaluationMutation = useMutation({
    mutationFn: async (targetIdeaId?: string) => {
      const activeId = targetIdeaId || ideaId;
      if (!activeId) throw new Error("No idea ID to evaluate");
      const headers = await getHeaders();
      const res = await api.post(`/ideas/${activeId}/evaluations`, { evaluation_type: "startup_evaluation" }, { headers });
      return res.data; // returns EvaluationResponse
    },
  });

  return {
    ideaQuery,
    ideasListQuery,
    saveIdeaMutation,
    triggerEvaluationMutation,
  };
};
