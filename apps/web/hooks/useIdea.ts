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

export function normalizeIdeaPayload(data: Partial<IdeaData>): Record<string, any> {
  const problem = data.problem_statement || data.core_problem || "No problem statement provided.";
  const solution = data.solution_description || data.elevator_pitch || "No solution description provided.";
  
  const customMetadata: Record<string, any> = {};
  if (data.elevator_pitch) customMetadata.elevator_pitch = data.elevator_pitch;
  if (data.core_problem) customMetadata.core_problem = data.core_problem;
  if (data.target_audience) customMetadata.target_audience = data.target_audience;
  if (data.existing_tech_stack) customMetadata.existing_tech_stack = data.existing_tech_stack;
  if (data.primary_platforms) customMetadata.primary_platforms = data.primary_platforms;
  if (data.monetization_model) customMetadata.monetization_model = data.monetization_model;
  if (data.key_competitors) customMetadata.key_competitors = data.key_competitors;
  if (data.technical_risks) customMetadata.technical_risks = data.technical_risks;

  const notesContent = data.notes || (Object.keys(customMetadata).length > 0 ? JSON.stringify(customMetadata) : null);

  return {
    title: data.title || (data.elevator_pitch ? data.elevator_pitch.slice(0, 50) : "Untitled Idea"),
    problem_statement: problem.length >= 10 ? problem : problem.padEnd(10, ' '),
    solution_description: solution.length >= 10 ? solution : solution.padEnd(10, ' '),
    target_users: data.target_users || data.target_audience || null,
    industry: data.industry || null,
    business_model: data.business_model || data.monetization_model || null,
    stage: data.stage || null,
    tags: data.tags || null,
    notes: notesContent,
    is_draft: data.is_draft ?? true,
  };
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
      const normalized = normalizeIdeaPayload(payload);
      const res = await api.post<IdeaData>(`/projects/${projectId}/ideas`, normalized, { headers });
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

