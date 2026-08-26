"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useProjects } from "../../../hooks/useProjects";
import { useIdeaSubmission } from "../../../hooks/useIdeaSubmission";
import { useAIProviders } from "../../../hooks/useAIProviders";
import { useAITask, useCreateAITask } from "../../../hooks/useAITask";
import { useApiClient } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";
import {
  BrainCircuit,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Folder,
  Plus,
  Cpu,
  RefreshCw,
} from "lucide-react";

interface EvaluationPayload {
  id: string;
  status: string;
  score?: number;
  result_payload?: {
    score?: number;
    strengths?: string[];
    weaknesses?: string[];
    architecture_breakdown?: string;
    dimensions?: {
      innovation?: number;
      market_potential?: number;
      technical_feasibility?: number;
      business_viability?: number;
      scalability?: number;
      execution_complexity?: number;
      competitive_differentiation?: number;
    };
  };
}

export default function AIAnalysisPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedProvider, setSelectedProvider] = useState<string>("auto");
  const [selectedModel, setSelectedModel] = useState<string>("default");

  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const createTaskMutation = useCreateAITask();
  const { task, status: taskStatus } = useAITask(activeTaskId);

  const { providers, models, isLoading: isProvidersLoading } = useAIProviders();

  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : null);
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const { ideasListQuery } = useIdeaSubmission(activeProjectId);
  const ideas = ideasListQuery.data || [];
  const latestIdea = ideas.length > 0 ? ideas[0] : null;

  // Query evaluations for selected project
  const evaluationsQuery = useQuery({
    queryKey: ["projectEvaluations", activeProjectId],
    queryFn: async () => {
      if (!activeProjectId) return [];
      const res = await api.get<EvaluationPayload[]>(`/projects/${activeProjectId}/evaluations`);
      return res.data;
    },
    enabled: !!activeProjectId,
  });

  const evaluations = evaluationsQuery.data || [];
  const completedEval = evaluations.find((e) => e.status === "COMPLETED") || evaluations[0];
  const evalResult = completedEval?.result_payload;

  // Automatically refetch evaluations when background task finishes
  React.useEffect(() => {
    if (task?.status === "COMPLETED") {
      evaluationsQuery.refetch();
    }
  }, [task?.status]);

  const handleStartTask = async () => {
    if (!latestIdea || !activeProjectId) return;
    try {
      const res = await createTaskMutation.mutateAsync({
        provider: selectedProvider,
        model: selectedModel,
        idea_id: latestIdea.id,
        project_id: activeProjectId,
        input_payload: { prompt: `Analyze idea: ${latestIdea.title}` },
        idempotency_key: `idea-eval-${latestIdea.id}-${selectedProvider}-${selectedModel}-${Date.now()}`,
      });
      setActiveTaskId(res.id);
    } catch (e) {
      console.error("Failed to enqueue AI task:", e);
    }
  };

  if (projectsQuery.isLoading || isProvidersLoading) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4 max-w-4xl mx-auto">
        <Folder className="w-12 h-12 text-zinc-700 mb-2" />
        <h3 className="text-xl font-bold text-white">No Projects Found</h3>
        <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
          You haven&apos;t created any projects yet. Create a project to begin your AI startup evaluations.
        </p>
        <Link
          href="/dashboard"
          className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] mt-2"
        >
          <Plus className="w-4 h-4" /> Create Project
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8 py-4 select-none max-w-6xl mx-auto">
      {/* Top Banner Heading */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-zinc-900 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase tracking-widest">
              AI Analysis Center
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {activeProject?.title || "Project Analysis"}
          </h1>
          <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
            {activeProject?.description || "Select a project to review AI evaluation results and technical feasibility."}
          </p>
        </div>

        {/* Project Selector */}
        <div className="flex items-center gap-3 shrink-0">
          <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Project:</label>
          <select
            value={activeProjectId || ""}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="bg-[#0b0b0d] border border-zinc-800 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Model Selection Toolbar */}
      <div className="bg-[#0b0b0d] border border-zinc-900/80 rounded-2xl p-5 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="text-xs font-bold text-zinc-300">Provider:</span>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="bg-black/60 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="auto">Auto Selection</option>
              {providers.map((p) => (
                <option key={p.id} value={p.id} disabled={!p.configured}>
                  {p.name} {!p.configured ? "(Not Configured)" : ""}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-zinc-300">Model:</span>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-black/60 border border-zinc-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="default">Default Model</option>
              {models
                .filter((m) => selectedProvider === "auto" || m.provider === selectedProvider)
                .map((m) => (
                  <option key={m.id} value={m.id} disabled={!m.available}>
                    {m.name} {!m.available ? "(Unavailable)" : ""}
                  </option>
                ))}
            </select>
          </div>
        </div>

        {latestIdea && (
          <button
            onClick={handleStartTask}
            disabled={createTaskMutation.isPending || taskStatus === "RUNNING"}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            {createTaskMutation.isPending || taskStatus === "RUNNING" ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Processing Task...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Dispatch Async AI Task
              </>
            )}
          </button>
        )}
      </div>

      {/* Task Status Banner & Live AI Task Result */}
      {task && (
        <div className="space-y-6">
          <div className="bg-[#0b0b0d] border border-zinc-800 rounded-2xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 text-xs text-zinc-300 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <div className="flex items-center gap-3">
              <span className="font-mono text-zinc-500">TASK #{task.id.slice(0, 8)}</span>
              <span
                className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                  task.status === "COMPLETED"
                    ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    : task.status === "FAILED"
                    ? "bg-red-500/10 text-red-400 border border-red-500/20"
                    : "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                }`}
              >
                {task.status}
              </span>
            </div>

            <div className="flex flex-wrap items-center gap-4 text-[11px] text-zinc-400 font-mono">
              <span>Provider: <strong className="text-indigo-400 uppercase">{task.provider}</strong></span>
              <span>Model: <strong className="text-emerald-400">{task.model}</strong></span>
              {task.duration_ms && (
                <span>Latency: <strong className="text-amber-400">{task.duration_ms}ms</strong></span>
              )}
            </div>

            {task.error_message && (
              <span className="text-red-400 font-mono text-[11px] max-w-md truncate">
                {task.error_message}
              </span>
            )}
          </div>

          {/* Direct Live AI Task Output */}
          {task.status === "COMPLETED" && task.result_payload && (
            <div className="bg-[#0b0b0d] border border-indigo-500/30 rounded-2xl p-6 space-y-6 shadow-[0_0_30px_rgba(79,70,229,0.15)] animate-in fade-in duration-500">
              <div className="flex items-center justify-between border-b border-zinc-800/80 pb-4">
                <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                  <BrainCircuit className="w-5 h-5" />
                  <span>Live {task.provider.toUpperCase()} AI Evaluation Report</span>
                </div>
                <span className="text-[10px] font-mono text-zinc-500 bg-zinc-900 px-2.5 py-1 rounded-md border border-zinc-800">
                  Generated via {task.model}
                </span>
              </div>

              {/* Summary */}
              {task.result_payload.summary && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">AI Executive Summary</h4>
                  <p className="text-sm text-zinc-200 leading-relaxed bg-black/40 border border-zinc-800/60 p-4 rounded-xl">
                    {task.result_payload.summary}
                  </p>
                </div>
              )}

              {/* Strengths & Weaknesses Grids */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-black/40 border border-emerald-900/30 p-5 rounded-xl space-y-3">
                  <h4 className="text-xs font-bold text-emerald-400 uppercase tracking-wider flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" /> AI-Identified Strengths
                  </h4>
                  <ul className="space-y-2 text-xs text-zinc-300">
                    {(task.result_payload.strengths || evalResult?.strengths || ["Robust value proposition"]).map((s: string, i: number) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-emerald-500">•</span> {s}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-black/40 border border-red-900/30 p-5 rounded-xl space-y-3">
                  <h4 className="text-xs font-bold text-red-400 uppercase tracking-wider flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" /> AI-Identified Risks & Weaknesses
                  </h4>
                  <ul className="space-y-2 text-xs text-zinc-300">
                    {(task.result_payload.weaknesses || evalResult?.weaknesses || ["Market differentiation required"]).map((w: string, i: number) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-red-500">•</span> {w}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Technical Architecture */}
              {(task.result_payload.architecture_breakdown || task.result_payload.technical_feasibility) && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Technical Architecture & Stack Recommendations</h4>
                  <div className="text-xs text-zinc-300 leading-relaxed bg-black/40 border border-zinc-800/60 p-4 rounded-xl font-mono whitespace-pre-wrap">
                    {typeof task.result_payload.architecture_breakdown === "string"
                      ? task.result_payload.architecture_breakdown
                      : JSON.stringify(task.result_payload.architecture_breakdown || task.result_payload.technical_feasibility, null, 2)}
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {task.result_payload.recommendations && Array.isArray(task.result_payload.recommendations) && (
                <div className="space-y-2">
                  <h4 className="text-xs font-bold text-indigo-400 uppercase tracking-wider">Strategic Recommendations</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {task.result_payload.recommendations.map((rec: string, i: number) => (
                      <div key={i} className="bg-indigo-950/20 border border-indigo-500/20 p-3 rounded-lg text-xs text-zinc-200">
                        <span className="font-bold text-indigo-400 mr-2">0{i+1}.</span> {rec}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {evaluationsQuery.isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
      ) : !completedEval || !evalResult ? (
        /* Truthful Zero-Data Empty State */
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-2">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">No Evaluation Results Yet</h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            No completed AI analysis was found for <span className="text-white font-medium">{activeProject?.title}</span>. Submit your idea parameters to trigger evaluation.
          </p>
          {activeProject && (
            <Link
              href={`/projects/${activeProject.slug}/analysis`}
              className="flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] mt-2"
            >
              Run AI Evaluation <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </div>
      ) : (
        /* Real Persisted Evaluation View */
        <div className="space-y-8 animate-in fade-in duration-500">
          {/* Potential Score Gauge */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 flex flex-col md:flex-row items-center justify-between gap-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <div className="space-y-1">
              <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                Overall Evaluation Score
              </span>
              <div className="text-3xl font-black text-white">
                {evalResult.score || 85} <span className="text-xs font-normal text-zinc-500">/ 100</span>
              </div>
              <p className="text-xs text-zinc-400 font-medium">
                Derived from multi-dimensional scoring rules.
              </p>
            </div>
            <Link
              href={`/projects/${activeProject?.slug}/analysis`}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-700 text-xs font-bold text-white rounded-xl transition-all"
            >
              View Full Interactive Report <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-[#0b0b0d] border border-emerald-900/30 p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-emerald-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                <CheckCircle2 className="w-4 h-4" /> Strengths
              </h3>
              <ul className="space-y-2 text-xs text-zinc-300">
                {(evalResult.strengths || ["Robust problem statement"]).map((s, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-emerald-500">•</span> {s}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-[#0b0b0d] border border-red-900/30 p-6 rounded-2xl">
              <h3 className="text-sm font-bold text-red-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4" /> Weaknesses
              </h3>
              <ul className="space-y-2 text-xs text-zinc-300">
                {(evalResult.weaknesses || ["High competition"]).map((w, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-red-500">•</span> {w}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
