"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useIdea } from "@/hooks/useIdea";
import { useApiClient } from "@/lib/api/client";
import {
  GitCompare,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Layers,
  ArrowRight,
  Sparkles,
  Zap,
  Award,
  RefreshCw,
  Plus
} from "lucide-react";

export interface IdeaComparisonItem {
  idea_id: string;
  project_id: string;
  title: string;
  problem_statement?: string;
  solution_description?: string;
  target_users?: string;
  industry?: string;
  business_model?: string;
  stage?: string;
  tags?: string;
  completeness_score: number;
  evaluation_status: "evaluated" | "unevaluated";
  evaluation_id?: string;
  overall_score?: number;
  score_delta?: number;
  rank?: number;
  dimensions: Record<string, number>;
  evaluated_at?: string;
}

export interface IdeaComparisonResponse {
  compared_count: number;
  highest_score_idea_id?: string;
  ideas: IdeaComparisonItem[];
  dimension_labels: Record<string, string>;
}

export default function ComparePage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects({ limit: 50 });
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>("llama-3.3-70b-versatile");

  // Automatically select first project when loaded
  React.useEffect(() => {
    if (!selectedProjectId && projects.length > 0) {
      setSelectedProjectId(projects[0].id);
    }
  }, [projects, selectedProjectId]);

  const { ideasQuery } = useIdea(selectedProjectId);
  const ideas = ideasQuery.data || [];

  const [selectedIdeaIds, setSelectedIdeaIds] = useState<string[]>([]);
  const [comparisonResult, setComparisonResult] = useState<IdeaComparisonResponse | null>(null);
  const [isComparing, setIsComparing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Toggle selection
  const handleToggleIdea = (ideaId: string) => {
    setErrorMsg(null);
    if (selectedIdeaIds.includes(ideaId)) {
      setSelectedIdeaIds(selectedIdeaIds.filter((id) => id !== ideaId));
    } else {
      if (selectedIdeaIds.length >= 5) {
        setErrorMsg("Maximum 5 ideas can be compared at once.");
        return;
      }
      setSelectedIdeaIds([...selectedIdeaIds, ideaId]);
    }
  };

  // Run Comparison
  const handleCompare = async () => {
    if (selectedIdeaIds.length < 2) {
      setErrorMsg("Select at least 2 ideas to compare.");
      return;
    }

    setIsComparing(true);
    setErrorMsg(null);

    try {
      const res = await api.post<IdeaComparisonResponse>("/evaluations/compare", {
        idea_ids: selectedIdeaIds,
        model: selectedModel
      });
      setComparisonResult(res.data);
    } catch (err: any) {
      console.error("Comparison error:", err);
      const detail = err?.response?.data?.detail || "Failed to compare selected ideas.";
      setErrorMsg(detail);
    } finally {
      setIsComparing(false);
    }
  };

  const highestScoreIdea = useMemo(() => {
    if (!comparisonResult?.ideas || comparisonResult.ideas.length === 0) return null;
    return [...comparisonResult.ideas].sort((a, b) => (b.overall_score || 0) - (a.overall_score || 0))[0];
  }, [comparisonResult]);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <GitCompare className="w-4 h-4" />
            <span>Multi-Concept Comparative Matrix</span>
            <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] px-2 py-0.5 rounded font-mono">⚡ Powered by Groq</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Compare Startup Ideas</h1>
          <p className="text-neutral-400 text-sm mt-1">
            Side-by-side multi-dimensional benchmarking and competitive gap analysis.
          </p>
        </div>

        {/* Project Selector & AI Model */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="bg-neutral-900 border border-neutral-800 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="llama-3.3-70b-versatile">Llama 3.3 70B Versatile (Groq)</option>
            <option value="qwen/qwen3.8-27b">Qwen 3.8 27B (Groq)</option>
            <option value="openai/gpt-oss-20b">GPT-OSS 20B (Groq)</option>
          </select>

          {projects.length > 0 && (
            <div className="flex items-center gap-3 bg-neutral-900 border border-neutral-800 rounded-lg p-2">
              <Layers className="w-4 h-4 text-neutral-400 ml-2" />
              <select
                value={selectedProjectId}
                onChange={(e) => {
                  setSelectedProjectId(e.target.value);
                  setSelectedIdeaIds([]);
                  setComparisonResult(null);
                  setErrorMsg(null);
                }}
                className="bg-transparent text-sm text-neutral-200 focus:outline-none cursor-pointer pr-4"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id} className="bg-neutral-900 text-neutral-200">
                    {p.title}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      {projectsQuery.isLoading ? (
        <div className="flex items-center justify-center py-20 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading workspace projects...</span>
        </div>
      ) : projects.length === 0 ? (
        /* Empty State: No Projects */
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <Layers className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-white">No Projects Available</h3>
          <p className="text-neutral-400 text-sm">
            You need at least one project with ideas to start comparing startup concepts.
          </p>
          <Link
            href="/projects/new"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Create First Project</span>
          </Link>
        </div>
      ) : ideasQuery.isLoading ? (
        <div className="flex items-center justify-center py-20 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Loading project ideas...</span>
        </div>
      ) : ideas.length === 0 ? (
        /* Empty State: No Ideas in Selected Project */
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <GitCompare className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-white">No Ideas in Selected Project</h3>
          <p className="text-neutral-400 text-sm">
            Add at least two ideas to this project to perform multi-dimensional comparison.
          </p>
          <Link
            href={`/projects/${selectedProjectId}/idea`}
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add New Idea</span>
          </Link>
        </div>
      ) : (
        /* Selector & Action Bar */
        <div className="space-y-6">
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">Select Ideas to Compare</h2>
                <p className="text-xs text-neutral-400 mt-0.5">Choose between 2 and 5 ideas from this project.</p>
              </div>
              <div className="text-xs font-mono px-3 py-1 bg-neutral-800 text-neutral-300 rounded-full border border-neutral-700">
                {selectedIdeaIds.length} / 5 Selected
              </div>
            </div>

            {/* Idea Selection Checklist */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {ideas.map((idea) => {
                const isSelected = selectedIdeaIds.includes(idea.id || "");
                return (
                  <div
                    key={idea.id}
                    onClick={() => idea.id && handleToggleIdea(idea.id)}
                    className={`p-4 rounded-lg border transition-all cursor-pointer flex items-start justify-between gap-3 ${
                      isSelected
                        ? "bg-indigo-950/40 border-indigo-500 text-white"
                        : "bg-neutral-950/60 border-neutral-800 hover:border-neutral-700 text-neutral-300"
                    }`}
                  >
                    <div className="space-y-1 pr-2">
                      <div className="font-medium text-sm text-white line-clamp-1">{idea.title}</div>
                      <p className="text-xs text-neutral-400 line-clamp-2">{idea.problem_statement || "No problem statement"}</p>
                      {idea.stage && (
                        <span className="inline-block text-[10px] uppercase font-mono px-2 py-0.5 bg-neutral-800 text-neutral-400 rounded mt-1">
                          {idea.stage}
                        </span>
                      )}
                    </div>
                    <div className={`w-5 h-5 rounded border flex items-center justify-center flex-shrink-0 mt-0.5 ${
                      isSelected ? "bg-indigo-600 border-indigo-600 text-white" : "border-neutral-700 bg-neutral-900"
                    }`}>
                      {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Error / Validation Banner */}
            {errorMsg && (
              <div className="bg-red-950/50 border border-red-800/80 rounded-lg p-3 flex items-center gap-2 text-red-300 text-sm">
                <AlertCircle className="w-4 h-4 flex-shrink-0 text-red-400" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Compare Action Button */}
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={handleCompare}
                disabled={selectedIdeaIds.length < 2 || isComparing}
                className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  selectedIdeaIds.length >= 2 && !isComparing
                    ? "bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-950/50 cursor-pointer"
                    : "bg-neutral-800 text-neutral-500 cursor-not-allowed border border-neutral-700/50"
                }`}
              >
                {isComparing ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span>Calculating Comparison Matrix...</span>
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    <span>Compare {selectedIdeaIds.length > 0 ? `(${selectedIdeaIds.length})` : ""} Ideas</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Results Display */}
          {comparisonResult && (
            <div className="space-y-8 animate-in fade-in duration-300">
              {/* Winner Banner */}
              {highestScoreIdea && (
                <div className="bg-gradient-to-r from-indigo-950/80 via-neutral-900 to-neutral-900 border border-indigo-800/60 rounded-xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400">
                      <Award className="w-6 h-6" />
                    </div>
                    <div>
                      <div className="text-xs uppercase font-mono tracking-wider text-indigo-400 font-semibold mb-1">
                        Highest Evaluated Score
                      </div>
                      <h3 className="text-2xl font-bold text-white">{highestScoreIdea.title}</h3>
                      <p className="text-xs text-neutral-400 mt-0.5">
                        Achieved top score of <span className="text-indigo-300 font-semibold">{highestScoreIdea.overall_score}/100</span> across evaluated criteria.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Idea Comparison Cards Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {comparisonResult.ideas.map((item) => (
                  <div
                    key={item.idea_id}
                    className={`bg-neutral-900 border rounded-xl p-6 space-y-5 flex flex-col justify-between ${
                      item.idea_id === comparisonResult.highest_score_idea_id
                        ? "border-indigo-500/80 ring-1 ring-indigo-500/30"
                        : "border-neutral-800"
                    }`}
                  >
                    <div className="space-y-4">
                      {/* Card Header */}
                      <div className="flex items-start justify-between gap-2 border-b border-neutral-800 pb-4">
                        <div>
                          {item.rank && (
                            <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-indigo-400 bg-indigo-950 border border-indigo-800/50 px-2 py-0.5 rounded">
                              Rank #{item.rank}
                            </span>
                          )}
                          <h3 className="text-xl font-bold text-white mt-1 line-clamp-1">{item.title}</h3>
                        </div>

                        {/* Overall Score Badge */}
                        {item.evaluation_status === "evaluated" && item.overall_score !== null ? (
                          <div className="text-right">
                            <div className="text-2xl font-black text-indigo-400">{item.overall_score}</div>
                            {item.score_delta !== undefined && item.score_delta !== null && (
                              <div className={`text-[10px] font-mono ${
                                item.score_delta === 0 ? "text-neutral-400" : "text-emerald-400"
                              }`}>
                                {item.score_delta === 0 ? "Top Score" : `${item.score_delta}`}
                              </div>
                            )}
                          </div>
                        ) : (
                          <div className="text-xs bg-amber-950/60 border border-amber-800/60 text-amber-300 px-2 py-1 rounded">
                            Unevaluated
                          </div>
                        )}
                      </div>

                      {/* Completeness Bar */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-xs text-neutral-400">
                          <span>Data Completeness</span>
                          <span className="font-mono text-neutral-200">{item.completeness_score}%</span>
                        </div>
                        <div className="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                            style={{ width: `${item.completeness_score}%` }}
                          />
                        </div>
                      </div>

                      {/* Key Attributes */}
                      <div className="space-y-2 text-xs">
                        <div className="text-neutral-400">
                          <span className="font-semibold text-neutral-300">Stage:</span>{" "}
                          <span className="capitalize">{item.stage || "Not specified"}</span>
                        </div>
                        <div className="text-neutral-400 line-clamp-2">
                          <span className="font-semibold text-neutral-300">Problem:</span>{" "}
                          {item.problem_statement || "No details provided"}
                        </div>
                      </div>
                    </div>

                    {/* Unevaluated Call-to-Action */}
                    {item.evaluation_status === "unevaluated" && (
                      <div className="bg-neutral-950 border border-neutral-800 rounded-lg p-3 text-center space-y-2">
                        <p className="text-xs text-neutral-400">Evaluation not available for this idea.</p>
                        <Link
                          href={`/projects/${item.project_id}/idea`}
                          className="inline-flex items-center justify-center gap-1.5 w-full bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium py-1.5 rounded transition-colors"
                        >
                          <span>Run Evaluation</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Dimensional Breakdown Matrix Table */}
              <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4 overflow-x-auto">
                <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    <span>Evaluation Dimensions Comparison</span>
                  </h3>
                </div>

                <table className="w-full text-left text-sm text-neutral-300">
                  <thead>
                    <tr className="border-b border-neutral-800 text-xs font-mono uppercase text-neutral-400">
                      <th className="py-3 px-4 min-w-[180px]">Dimension</th>
                      {comparisonResult.ideas.map((item) => (
                        <th key={item.idea_id} className="py-3 px-4 min-w-[160px]">
                          {item.title}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-800/60">
                    {Object.entries(comparisonResult.dimension_labels).map(([key, label]) => (
                      <tr key={key} className="hover:bg-neutral-800/30">
                        <td className="py-3 px-4 font-medium text-neutral-200">{label}</td>
                        {comparisonResult.ideas.map((item) => {
                          const val = item.dimensions[key];
                          return (
                            <td key={item.idea_id} className="py-3 px-4">
                              {item.evaluation_status === "evaluated" && val !== undefined ? (
                                <div className="flex items-center gap-2">
                                  <div className="w-12 bg-neutral-800 h-2 rounded-full overflow-hidden">
                                    <div
                                      className="h-full bg-indigo-400"
                                      style={{ width: `${Math.min(val, 100)}%` }}
                                    />
                                  </div>
                                  <span className="font-mono text-xs text-neutral-200">{val}</span>
                                </div>
                              ) : (
                                <span className="text-xs text-neutral-500 italic">N/A</span>
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
