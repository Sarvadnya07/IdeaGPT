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

      {projectsQuery.isLoading || evaluationsQuery.isLoading ? (
        <div className="flex items-center justify-center py-16 text-neutral-400 gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
          <span className="text-xs">Loading project reports...</span>
        </div>
      ) : completedEvals.length === 0 ? (
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
    </div>
  );
}
