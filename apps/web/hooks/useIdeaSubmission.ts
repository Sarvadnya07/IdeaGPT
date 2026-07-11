import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@clerk/nextjs";
import axios from "axios";
import { useEffect, useState } from "react";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
});

export interface IdeaData {
  problem_statement?: string;
  solution_description?: string;
  target_audience?: string;
  business_model?: string;
  competitors?: string;
  unique_selling_proposition?: string;
  technology_stack?: string;
  budget?: string;
  timeline?: string;
  additional_notes?: string;
}

export const useIdeaSubmission = (projectId: number | null) => {
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
      const res = await api.get(`/projects/${projectId}/idea`, { headers });
      return res.data;
    },
    enabled: !!projectId,
  });

  const saveIdeaMutation = useMutation({
    mutationFn: async (data: IdeaData) => {
      if (!projectId) throw new Error("No project ID");
      const headers = await getHeaders();
      const res = await api.post(`/projects/${projectId}/idea`, data, { headers });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["idea", projectId] });
    },
  });

  const triggerEvaluationMutation = useMutation({
    mutationFn: async () => {
      if (!projectId) throw new Error("No project ID");
      const headers = await getHeaders();
      const res = await api.post(`/projects/${projectId}/evaluate`, {}, { headers });
      return res.data; // returns EvaluationJobResponse
    },
  });

  return {
    ideaQuery,
    saveIdeaMutation,
    triggerEvaluationMutation,
  };
};
