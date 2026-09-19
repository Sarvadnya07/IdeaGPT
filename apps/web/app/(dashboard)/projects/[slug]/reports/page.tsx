"use client";

import React, { use } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import { useQuery } from "@tanstack/react-query";
import {
  FileText,
  ArrowRight,
  RefreshCw,
  Download,
  FileCode,
  Sparkles,
} from "lucide-react";
import { toast } from "sonner";

interface EvaluationItem {
  id: string;
  project_id: string;
  idea_id: string;
  status: string;
  created_at: string;
  result_payload: {
    score?: number;
    summary?: string;
    strengths?: string[];
    weaknesses?: string[];
    recommendations?: string[];
    architecture_breakdown?: string;
  };
}

/**
 * A durably persisted AI artifact (PRODUCT-01 P-01).
 *
 * These were previously written by every generator but never read back by any
 * page, so generated PRDs / blueprints / lab outputs vanished from the product
 * on refresh while remaining in the database.
 */
interface AIArtifactItem {
  id: string;
  artifact_type: string;
  title?: string | null;
  project_id?: string | null;
  idea_id?: string | null;
  provider?: string | null;
  model?: string | null;
  execution_type?: string | null;
  fallback_used?: boolean;
  content_payload?: Record<string, unknown> | null;
  created_at?: string | null;
}

const ARTIFACT_LABELS: Record<string, string> = {
  roadmap: "Roadmap",
  tech_stack: "Tech Stack",
  architecture: "Architecture Blueprint",
  prd: "Product Requirements Doc",
  pitch_deck: "Pitch Deck",
  github_lab: "GitHub Blueprint",
  investor_lab: "Investor Analysis",
  mentor_lab: "Mentor Session",
  recruiter_lab: "Recruiting Plan",
  strategy_lab: "Strategy Analysis",
};

export default function ProjectReportsPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const project = projectsQuery.data?.items.find((p) => p.slug === slug);

  // Query evaluations for this specific project
  const evaluationsQuery = useQuery({
    queryKey: ["projectSpecificEvaluations", project?.id],
    queryFn: async () => {
      if (!project?.id) return [];
      const res = await api.get<EvaluationItem[]>(
        `/projects/${project.id}/evaluations`,
      );
      return res.data;
    },
    enabled: !!project?.id,
  });

  const evaluations = evaluationsQuery.data || [];
  const completedEvals = evaluations.filter((e) => e.status === "COMPLETED");

  // PRODUCT-01 P-01: read back the durable artifacts generated for this project.
  const artifactsQuery = useQuery({
    queryKey: ["projectArtifacts", project?.id],
    queryFn: async () => {
      if (!project?.id) return [];
      const res = await api.get<AIArtifactItem[]>("/ai/artifacts", {
        params: { project_id: project.id, limit: 100 },
      });
      return res.data;
    },
    enabled: !!project?.id,
  });

  const artifacts = artifactsQuery.data || [];
  const [expandedArtifactId, setExpandedArtifactId] = React.useState<
    string | null
  >(null);

  const handleDownloadArtifactJson = (item: AIArtifactItem) => {
    const blob = new Blob(
      [JSON.stringify(item.content_payload ?? {}, null, 2)],
      { type: "application/json" },
    );
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${item.artifact_type}-${item.id}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Artifact JSON downloaded!");
  };

  const handleDownloadMarkdown = (item: EvaluationItem) => {
    const payload = item.result_payload || {};
    const title = project?.title || "Startup Idea";
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-xs mb-1">
            <FileText className="w-3.5 h-3.5" />
            <span>Project Reports & Documents</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            {project?.title ? `${project.title} Reports` : "Reports"}
          </h1>
          <p className="text-neutral-400 text-xs mt-0.5">
            Evaluation summaries, pitch documents, and technical reports
            generated for this project.
          </p>
        </div>

        <Link
          href="/reports"
          className="inline-flex items-center gap-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium px-3.5 py-2 rounded-lg transition-colors border border-neutral-700"
        >
          <span>All Workspace Reports</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {projectsQuery.isLoading ||
      evaluationsQuery.isLoading ||
      artifactsQuery.isLoading ? (
        <div className="flex items-center justify-center py-16 text-neutral-400 gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
          <span className="text-xs">Loading project reports...</span>
        </div>
      ) : completedEvals.length === 0 && artifacts.length === 0 ? (
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 text-center max-w-lg mx-auto my-8 space-y-4">
          <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-semibold text-white">
            No Reports Generated Yet
          </h3>
          <p className="text-neutral-400 text-xs">
            Run an AI evaluation on ideas within{" "}
            <span className="text-neutral-200 font-semibold">
              {project?.title}
            </span>{" "}
            to generate and export reports.
          </p>
          <div className="flex items-center justify-center gap-3 pt-2">
            <Link
              href={`/projects/${slug}/analysis`}
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <span>Run AI Evaluation</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {completedEvals.map((item, idx) => {
            const score = item.result_payload?.score || 75;
            return (
              <div
                key={item.id}
                className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs border-b border-neutral-800 pb-2">
                    <span className="font-mono text-indigo-400 font-bold">
                      Report #{idx + 1}
                    </span>
                    <span className="text-emerald-400 font-bold flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" /> {score} / 100
                    </span>
                  </div>
                  <p className="text-xs text-neutral-300 line-clamp-2">
                    {item.result_payload?.summary ||
                      "Completed idea feasibility evaluation."}
                  </p>
                  <div className="text-[10px] font-mono text-neutral-500">
                    {new Date(item.created_at).toLocaleDateString()}
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 pt-2 border-t border-neutral-800/80">
                  <button
                    onClick={() => handleDownloadMarkdown(item)}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-indigo-950 hover:bg-indigo-900 border border-indigo-800 text-indigo-300 text-xs rounded-lg transition-colors"
                  >
                    <Download className="w-3 h-3" />
                    <span>.MD</span>
                  </button>
                  <button
                    onClick={() => handleDownloadJson(item)}
                    className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-300 text-xs rounded-lg transition-colors"
                  >
                    <FileCode className="w-3 h-3" />
                    <span>.JSON</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Durable AI artifacts (PRODUCT-01 P-01)                              */}
      {/* Previously write-only: generated blueprints/PRDs/labs were stored   */}
      {/* but no page read them back.                                        */}
      {/* ------------------------------------------------------------------ */}
      {artifacts.length > 0 && (
        <section className="space-y-3">
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold text-white">
              Generated Artifacts
            </h2>
            <span className="text-[10px] font-mono bg-neutral-800 text-neutral-400 px-2 py-0.5 rounded">
              {artifacts.length}
            </span>
          </div>

          <div className="space-y-2">
            {artifacts.map((item) => {
              const isOpen = expandedArtifactId === item.id;
              const label =
                ARTIFACT_LABELS[item.artifact_type] || item.artifact_type;
              return (
                <div
                  key={item.id}
                  className="bg-neutral-900 border border-neutral-800 rounded-xl overflow-hidden"
                >
                  <div className="flex flex-wrap items-center justify-between gap-3 p-4">
                    <div className="min-w-0 space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-[10px] font-bold uppercase tracking-wider bg-indigo-950 border border-indigo-800 text-indigo-300 px-2 py-0.5 rounded">
                          {label}
                        </span>
                        {item.fallback_used && (
                          <span
                            className="text-[10px] font-bold uppercase tracking-wider bg-amber-950 border border-amber-800 text-amber-300 px-2 py-0.5 rounded"
                            title="The AI provider was unavailable; this output came from the deterministic rule-based engine."
                          >
                            Rule-based fallback
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-neutral-200 font-medium truncate">
                        {item.title || "Untitled artifact"}
                      </p>
                      <div className="text-[10px] font-mono text-neutral-500 flex flex-wrap gap-x-3">
                        {item.provider && <span>{item.provider}</span>}
                        {item.model && <span>{item.model}</span>}
                        {item.created_at && (
                          <span>
                            {new Date(item.created_at).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <button
                        onClick={() =>
                          setExpandedArtifactId(isOpen ? null : item.id)
                        }
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-300 text-xs rounded-lg transition-colors"
                      >
                        {isOpen ? "Hide" : "View"}
                      </button>
                      <button
                        onClick={() => handleDownloadArtifactJson(item)}
                        className="inline-flex items-center gap-1 px-2.5 py-1.5 bg-neutral-800 hover:bg-neutral-700 border border-neutral-700 text-neutral-300 text-xs rounded-lg transition-colors"
                      >
                        <FileCode className="w-3 h-3" />
                        <span>.JSON</span>
                      </button>
                    </div>
                  </div>

                  {isOpen && (
                    <pre className="border-t border-neutral-800 bg-black/40 p-4 text-[11px] text-neutral-300 font-mono overflow-x-auto max-h-96">
                      {JSON.stringify(item.content_payload ?? {}, null, 2)}
                    </pre>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}
    </div>
  );
}
