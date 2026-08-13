"use client";

import React, { use } from "react";
import Link from "next/link";
import { useProjectBySlug } from "@/hooks/useProjects";
import { useEvaluationHistory } from "@/hooks/useEvaluationHistory";
import { FileText, Download, ArrowRight, RefreshCw, Calendar, CheckCircle2 } from "lucide-react";

export default function ProjectReportsPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const { projectQuery } = useProjectBySlug(slug);
  const project = projectQuery.data;

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
            Evaluation summaries, pitch documents, and technical reports generated for this project.
          </p>
        </div>

        <Link
          href="/reports"
          className="inline-flex items-center gap-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium px-3.5 py-2 rounded-lg transition-colors border border-neutral-700"
        >
          <span>All Saved Reports</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

      {projectQuery.isLoading ? (
        <div className="flex items-center justify-center py-16 text-neutral-400 gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
          <span className="text-xs">Loading project reports...</span>
        </div>
      ) : (
        <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-8 text-center max-w-lg mx-auto my-8 space-y-4">
          <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <FileText className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-semibold text-white">Project Reports Dashboard</h3>
          <p className="text-neutral-400 text-xs">
            Run an evaluation or export analysis reports for ideas in <span className="text-neutral-200 font-semibold">{project?.title}</span>.
          </p>
          <div className="flex items-center justify-center gap-3 pt-2">
            <Link
              href={`/projects/${slug}/analysis`}
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors"
            >
              <span>View AI Analysis</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
