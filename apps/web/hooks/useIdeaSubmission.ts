import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api/client";

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

export function normalizeIdeaPayload(
  data: Partial<IdeaData>,
): Record<string, any> {
  return {
    title: data.title || "Untitled Idea",
    problem_statement:
      data.problem_statement && data.problem_statement.length >= 10
        ? data.problem_statement
        : data.problem_statement
          ? data.problem_statement.padEnd(10, " ")
          : "No problem statement provided.",
    solution_description:
      data.solution_description && data.solution_description.length >= 10
        ? data.solution_description
        : data.solution_description
          ? data.solution_description.padEnd(10, " ")
          : "No solution description provided.",
    target_users: data.target_users || data.target_audience || null,
    industry: data.industry || null,
    business_model: data.business_model || null,
    stage: data.stage || null,
    tags: data.tags || null,
    notes:
      data.notes ||
      data.additional_notes ||
      (data.unique_selling_proposition ||
      data.technology_stack ||
      data.budget ||
      data.timeline
        ? JSON.stringify({
            usp: data.unique_selling_proposition,
            tech_stack: data.technology_stack,
            budget: data.budget,
            timeline: data.timeline,
          })
        : null),
    is_draft: data.is_draft ?? true,
  };
}

export const useIdeaSubmission = (
  projectId: string | null,
  ideaId: string | null = null,
) => {
  const api = useApiClient();
  const queryClient = useQueryClient();

  const ideaQuery = useQuery({
    queryKey: ["idea", ideaId],
    queryFn: async () => {
      if (!ideaId) return null;
      const res = await api.get<IdeaData>(`/ideas/${ideaId}`);
      return res.data;
    },
    enabled: !!ideaId,
  });

  const ideasListQuery = useQuery({
    queryKey: ["ideas", projectId],
    queryFn: async () => {
      if (!projectId) return [];
      const res = await api.get<IdeaData[]>(`/projects/${projectId}/ideas`);
      return res.data;
    },
    enabled: !!projectId,
  });

  const saveIdeaMutation = useMutation({
    mutationFn: async (data: Partial<IdeaData>) => {
      const payload = normalizeIdeaPayload(data);

      if (ideaId) {
        // Update existing
        const res = await api.patch<IdeaData>(`/ideas/${ideaId}`, payload);
        return res.data;
      } else {
        // Create new
        if (!projectId) throw new Error("No project ID for new idea creation");
        const res = await api.post<IdeaData>(
          `/projects/${projectId}/ideas`,
          payload,
        );
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
      const res = await api.post(`/ideas/${activeId}/evaluations`, {
        evaluation_type: "startup_evaluation",
      });
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
