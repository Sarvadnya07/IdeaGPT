"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";
import {
  FileText,
  Download,
  Eye,
  RefreshCw,
  Plus,
  Layers,
  ArrowRight,
  Sparkles,
  Copy,
  Check,
  Filter,
  FileCode,
  FileSpreadsheet,
} from "lucide-react";
import { toast } from "sonner";

interface EvaluationItem {
  id: string;
  project_id: string;
  idea_id: string;
  evaluation_type: string;
  status: string;
  created_at: string;
  result_payload: {
    score?: number;
    summary?: string;
    strengths?: string[];
    weaknesses?: string[];
    recommendations?: string[];
    architecture_breakdown?: string;
    dimensions?: Record<string, number>;
  };
}

export default function ReportsPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects({ limit: 50 });
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [activePreviewEval, setActivePreviewEval] =
    useState<EvaluationItem | null>(null);
  const [previewMode, setPreviewMode] = useState<"markdown" | "json">(
    "markdown",
  );
  const [isCopied, setIsCopied] = useState(false);

  // Active project ID
  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");

  // Query evaluations for the active project
  const evaluationsQuery = useQuery({
    queryKey: ["projectEvaluationsReport", activeProjectId],
    queryFn: async () => {
      if (!activeProjectId) return [];
      const res = await api.get<EvaluationItem[]>(
        `/projects/${activeProjectId}/evaluations`,
      );
      return res.data;
    },
    enabled: !!activeProjectId,
  });

  const evaluations = evaluationsQuery.data || [];
  const completedEvaluations = evaluations.filter(
    (e) => e.status === "COMPLETED",
  );

  const activeProject = projects.find((p) => p.id === activeProjectId);

  // Download handlers
  const handleDownloadMarkdown = (item: EvaluationItem) => {
    const payload = item.result_payload || {};
    const title = activeProject?.title || "Startup Idea";
    const score = payload.score || 70;
    const summary = payload.summary || "No summary available.";
    const strengths = (payload.strengths || []).map((s) => `- ${s}`).join("\n");
    const weaknesses = (payload.weaknesses || [])
      .map((w) => `- ${w}`)
      .join("\n");
    const recommendations = (payload.recommendations || [])
      .map((r) => `- ${r}`)
      .join("\n");
    const arch =
      payload.architecture_breakdown || "Standard modular architecture.";

    const mdContent = `# AI Idea Evaluation Report: ${title}
**Evaluation ID**: \`${item.id}\`  
**Overall Score**: ${score} / 100  
**Generated**: ${new Date(item.created_at).toLocaleDateString()}  

---

## 1. Executive Summary
${summary}

---

## 2. Key Strengths
${strengths || "- Robust concept definition"}

---

## 3. Critical Weaknesses & Risks
${weaknesses || "- Competitive saturation risks"}

---

## 4. Strategic Recommendations
${recommendations || "- Develop modular MVP"}

---

## 5. Technical Architecture & Feasibility
${arch}
`;

    const blob = new Blob([mdContent], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}-evaluation.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Markdown report downloaded!");
  };

  const handleDownloadJson = (item: EvaluationItem) => {
    const blob = new Blob([JSON.stringify(item.result_payload, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `evaluation-${item.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("JSON evaluation payload downloaded!");
  };

  const handleCopyContent = (text: string) => {
    navigator.clipboard.writeText(text);
    setIsCopied(true);
    toast.success("Copied report to clipboard!");
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <FileText className="w-4 h-4" />
            <span>Reports & Exports Center</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Project Reports
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Review, preview, and download full evaluation reports and
            architecture summaries.
          </p>
        </div>

        {/* Project Selector */}
        {projects.length > 0 && (
          <div className="flex items-center gap-3 bg-neutral-900 border border-neutral-800 rounded-lg p-2">
            <Layers className="w-4 h-4 text-neutral-400 ml-2" />
            <select
              value={activeProjectId}
              onChange={(e) => {
                setSelectedProjectId(e.target.value);
                setActivePreviewEval(null);
              }}
              className="bg-transparent text-sm text-neutral-200 focus:outline-none cursor-pointer pr-4"
            >
              {projects.map((p) => (
                <option
                  key={p.id}
                  value={p.id}
                  className="bg-neutral-900 text-neutral-200"
                >
                  {p.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      {projectsQuery.isLoading ? (
        <div className="flex items-center justify-center py-20 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Loading projects...</span>
        </div>
      ) : projects.length === 0 ? (
        /* Empty State: No Projects */
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <Layers className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-white">
            No Projects Found
          </h3>
          <p className="text-neutral-400 text-sm">
            Create your first project to begin generating evaluation reports and
            summaries.
          </p>
          <Link
            href="/projects/new"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Create Project</span>
          </Link>
        </div>
      ) : evaluationsQuery.isLoading ? (
        <div className="flex items-center justify-center py-20 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Loading project evaluation records...</span>
        </div>
      ) : completedEvaluations.length === 0 ? (
        /* Empty State: No Completed Evaluations */
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <FileText className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-white">
            No Completed Reports for {activeProject?.title}
          </h3>
          <p className="text-neutral-400 text-sm">
            Run an AI evaluation on ideas within this project to generate
            downloadable reports.
          </p>
          {activeProject && (
            <Link
              href={`/projects/${activeProject.slug}/analysis`}
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <span>Run AI Evaluation</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          )}
        </div>
      ) : (
        /* Populated State: Reports List Grid */
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {completedEvaluations.map((item, idx) => {
              const res = item.result_payload || {};
              const score = res.score || 75;

              return (
                <div
                  key={item.id}
                  className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-5 flex flex-col justify-between hover:border-neutral-700 transition-all shadow-md"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
                      <span className="text-xs font-mono font-bold text-indigo-400 uppercase tracking-wider">
                        Report #{idx + 1}
                      </span>
                      <div className="flex items-center gap-1.5 font-bold text-lg text-emerald-400">
                        <Sparkles className="w-4 h-4" />
                        <span>{score} / 100</span>
                      </div>
                    </div>

                    <h3 className="text-base font-bold text-white">
                      {activeProject?.title} Evaluation
                    </h3>
                    <p className="text-xs text-neutral-400 line-clamp-3 leading-relaxed">
                      {res.summary ||
                        "Comprehensive multidimensional evaluation summary."}
                    </p>

                    <div className="text-[11px] font-mono text-neutral-500 pt-1">
                      Evaluated:{" "}
                      {new Date(item.created_at).toLocaleDateString()}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="pt-4 border-t border-neutral-800/80 flex items-center justify-between gap-2">
                    <button
                      onClick={() => setActivePreviewEval(item)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium rounded-lg transition-colors"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Preview</span>
                    </button>

                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleDownloadMarkdown(item)}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-indigo-950/80 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 text-xs font-medium rounded-lg transition-colors"
                        title="Download Markdown (.md)"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>.MD</span>
                      </button>
                      <button
                        onClick={() => handleDownloadJson(item)}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-300 text-xs font-medium rounded-lg transition-colors"
                        title="Download JSON Payload (.json)"
                      >
                        <FileCode className="w-3.5 h-3.5" />
                        <span>.JSON</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Preview Modal */}
      {activePreviewEval && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-in fade-in duration-200">
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
            {/* Modal Header */}
            <div className="p-5 border-b border-neutral-800 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-bold text-white">
                  {activeProject?.title} — Report Preview
                </h3>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center bg-neutral-950 border border-neutral-800 rounded-lg p-1 text-xs">
                  <button
                    onClick={() => setPreviewMode("markdown")}
                    className={`px-3 py-1 rounded-md transition-colors ${
                      previewMode === "markdown"
                        ? "bg-indigo-600 text-white"
                        : "text-neutral-400 hover:text-white"
                    }`}
                  >
                    Formatted
                  </button>
                  <button
                    onClick={() => setPreviewMode("json")}
                    className={`px-3 py-1 rounded-md transition-colors ${
                      previewMode === "json"
                        ? "bg-indigo-600 text-white"
                        : "text-neutral-400 hover:text-white"
                    }`}
                  >
                    JSON
                  </button>
                </div>

                <button
                  onClick={() => setActivePreviewEval(null)}
                  className="text-neutral-400 hover:text-white text-sm font-semibold p-1"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 text-sm text-neutral-300">
              {previewMode === "markdown" ? (
                <div className="space-y-6">
                  {/* Score & Summary */}
                  <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-5 space-y-2">
                    <div className="text-xs font-mono text-indigo-400 uppercase tracking-widest">
                      Overall Feasibility Score:{" "}
                      {activePreviewEval.result_payload?.score || 75} / 100
                    </div>
                    <p className="text-neutral-300 leading-relaxed text-sm">
                      {activePreviewEval.result_payload?.summary ||
                        "No executive summary available."}
                    </p>
                  </div>

                  {/* Strengths & Weaknesses Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-emerald-950/20 border border-emerald-900/40 rounded-xl p-4 space-y-2">
                      <h4 className="font-bold text-xs uppercase tracking-wider text-emerald-400">
                        Key Strengths
                      </h4>
                      <ul className="space-y-1 text-xs text-neutral-300">
                        {(
                          activePreviewEval.result_payload?.strengths || [
                            "Robust problem domain",
                          ]
                        ).map((s, i) => (
                          <li key={i}>• {s}</li>
                        ))}
                      </ul>
                    </div>

                    <div className="bg-red-950/20 border border-red-900/40 rounded-xl p-4 space-y-2">
                      <h4 className="font-bold text-xs uppercase tracking-wider text-red-400">
                        Risks & Weaknesses
                      </h4>
                      <ul className="space-y-1 text-xs text-neutral-300">
                        {(
                          activePreviewEval.result_payload?.weaknesses || [
                            "Market saturation risks",
                          ]
                        ).map((w, i) => (
                          <li key={i}>• {w}</li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4 space-y-2">
                    <h4 className="font-bold text-xs uppercase tracking-wider text-indigo-400">
                      Strategic Recommendations
                    </h4>
                    <ul className="space-y-1 text-xs text-neutral-300">
                      {(
                        activePreviewEval.result_payload?.recommendations || [
                          "Develop modular MVP",
                        ]
                      ).map((r, i) => (
                        <li key={i}>• {r}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Architecture Breakdown */}
                  <div className="bg-neutral-950 border border-neutral-800 rounded-xl p-4 space-y-2">
                    <h4 className="font-bold text-xs uppercase tracking-wider text-amber-400">
                      Technical Architecture & Feasibility
                    </h4>
                    <p className="text-xs text-neutral-300 leading-relaxed font-mono">
                      {activePreviewEval.result_payload
                        ?.architecture_breakdown ||
                        "Standard modular microservices architecture."}
                    </p>
                  </div>
                </div>
              ) : (
                <pre className="bg-neutral-950 border border-neutral-800 p-4 rounded-xl text-xs font-mono text-neutral-300 overflow-x-auto">
                  {JSON.stringify(activePreviewEval.result_payload, null, 2)}
                </pre>
              )}
            </div>

            {/* Modal Footer */}
            <div className="p-4 border-t border-neutral-800 flex items-center justify-between bg-neutral-950/60">
              <button
                onClick={() =>
                  handleCopyContent(
                    previewMode === "markdown"
                      ? JSON.stringify(
                          activePreviewEval.result_payload?.summary || "",
                        )
                      : JSON.stringify(
                          activePreviewEval.result_payload,
                          null,
                          2,
                        ),
                  )
                }
                className="inline-flex items-center gap-1.5 text-xs text-neutral-400 hover:text-white transition-colors"
              >
                {isCopied ? (
                  <Check className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
                <span>{isCopied ? "Copied!" : "Copy Payload"}</span>
              </button>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleDownloadMarkdown(activePreviewEval)}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download Markdown</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
