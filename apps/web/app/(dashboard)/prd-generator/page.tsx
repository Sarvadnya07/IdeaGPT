"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import {
  FileText,
  Layers,
  Sparkles,
  RefreshCw,
  Download,
  Copy,
  Check,
  CheckCircle2,
  ListOrdered,
  Users,
  Target,
  ArrowRight
} from "lucide-react";
import { toast } from "sonner";

interface PRDResponse {
  title: string;
  version: string;
  status: string;
  category: string;
  target_users: string;
  executive_summary: string;
  problem_definition: {
    core_problem: string;
    current_alternatives: string[];
    why_now: string;
  };
  user_personas: Array<{
    persona: string;
    need: string;
  }>;
  functional_requirements: Array<{
    id: string;
    feature: string;
    priority: string;
    description: string;
  }>;
  non_functional_requirements: Array<{
    id: string;
    category: string;
    target: string;
  }>;
  success_metrics: Array<{
    metric: string;
    target: string;
  }>;
}

export default function PRDGeneratorPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects({ limit: 50 });
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [prdData, setPrdData] = useState<PRDResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const fetchPRD = async (title: string, category: string, description: string) => {
    setIsLoading(true);
    try {
      const res = await api.post<PRDResponse>("/ai/prd", {
        title: title || "Startup Concept",
        category: category || "B2B SaaS",
        problem_statement: description || "Founders lack rapid technical feasibility validation.",
        solution_description: "Automated AI co-founder for technical architecture scoping and validation.",
        target_users: "Startup Founders, Product Managers, Engineers"
      });
      setPrdData(res.data);
    } catch (err) {
      console.error("Failed to load PRD:", err);
      toast.error("Failed to generate PRD.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeProject) {
      fetchPRD(activeProject.title, activeProject.category || "B2B SaaS", activeProject.description || "");
    } else if (projects.length === 0 && !projectsQuery.isLoading) {
      fetchPRD("Nexus AI", "B2B SaaS", "AI platform validation");
    }
  }, [activeProjectId]);

  const handleDownloadMarkdown = () => {
    if (!prdData) return;
    const md = `# ${prdData.title}
**Version**: ${prdData.version} | **Status**: ${prdData.status} | **Category**: ${prdData.category}  

---

## Executive Summary
${prdData.executive_summary}

---

## Problem Definition
- **Core Problem**: ${prdData.problem_definition.core_problem}
- **Current Alternatives**: ${prdData.problem_definition.current_alternatives.join(", ")}
- **Why Now**: ${prdData.problem_definition.why_now}

---

## User Personas
${prdData.user_personas.map((p) => `### ${p.persona}\n${p.need}`).join("\n\n")}

---

## Functional Requirements
| ID | Feature | Priority | Description |
| :--- | :--- | :--- | :--- |
${prdData.functional_requirements.map((f) => `| ${f.id} | ${f.feature} | ${f.priority} | ${f.description} |`).join("\n")}

---

## Non-Functional Requirements
| ID | Category | Target Metric |
| :--- | :--- | :--- |
${prdData.non_functional_requirements.map((n) => `| ${n.id} | ${n.category} | ${n.target} |`).join("\n")}

---

## Success Metrics (KPIs)
${prdData.success_metrics.map((m) => `- **${m.metric}**: ${m.target}`).join("\n")}
`;

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${prdData.title.toLowerCase().replace(/[^a-z0-9]+/g, "-")}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("PRD Markdown downloaded!");
  };

  const handleCopy = () => {
    if (!prdData) return;
    navigator.clipboard.writeText(JSON.stringify(prdData, null, 2));
    setIsCopied(true);
    toast.success("Copied PRD to clipboard!");
    setTimeout(() => setIsCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <FileText className="w-4 h-4" />
            <span>Product Specifications & Planning</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">PRD Generator</h1>
          <p className="text-neutral-400 text-sm mt-1">
            Automated Product Requirements Documents with user personas, functional specs, and success KPIs.
          </p>
        </div>

        {/* Project Selector & Actions */}
        <div className="flex items-center gap-3">
          {projects.length > 0 && (
            <div className="flex items-center gap-2 bg-neutral-900 border border-neutral-800 rounded-lg p-2">
              <Layers className="w-4 h-4 text-neutral-400 ml-1" />
              <select
                value={activeProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                className="bg-transparent text-xs text-neutral-200 focus:outline-none cursor-pointer pr-2"
              >
                {projects.map((p) => (
                  <option key={p.id} value={p.id} className="bg-neutral-900 text-neutral-200">
                    {p.title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {prdData && (
            <button
              onClick={handleDownloadMarkdown}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-colors shadow-lg shadow-indigo-950/50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download PRD</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Generating structured Product Requirements Document...</span>
        </div>
      ) : !prdData ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <FileText className="w-12 h-12 text-neutral-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">No PRD Available</h3>
          <p className="text-xs text-neutral-400">Select a project to generate PRD specifications.</p>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-300 max-w-5xl mx-auto">
          {/* PRD Title Card */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-neutral-800 pb-4">
              <div>
                <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-indigo-400">
                  {prdData.version} • {prdData.status}
                </span>
                <h2 className="text-2xl font-bold text-white mt-1">{prdData.title}</h2>
              </div>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-300 text-xs font-medium rounded-lg transition-colors w-fit"
              >
                {isCopied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{isCopied ? "Copied!" : "Copy JSON"}</span>
              </button>
            </div>

            <div className="space-y-2">
              <h3 className="text-xs uppercase font-bold text-neutral-400 tracking-wider">Executive Summary</h3>
              <p className="text-xs text-neutral-300 leading-relaxed">{prdData.executive_summary}</p>
            </div>
          </div>

          {/* User Personas */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center gap-2 border-b border-neutral-800 pb-3">
              <Users className="w-4 h-4 text-indigo-400" />
              <h3 className="font-bold text-sm text-white">Target User Personas</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
              {prdData.user_personas.map((p, i) => (
                <div key={i} className="bg-neutral-950 border border-neutral-800/80 rounded-xl p-4 space-y-1.5">
                  <div className="font-bold text-xs text-white">{p.persona}</div>
                  <p className="text-xs text-neutral-400 leading-relaxed">{p.need}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Functional Requirements */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4 overflow-x-auto">
            <div className="flex items-center gap-2 border-b border-neutral-800 pb-3">
              <ListOrdered className="w-4 h-4 text-emerald-400" />
              <h3 className="font-bold text-sm text-white">Functional Requirements Specification</h3>
            </div>
            <table className="w-full text-left text-xs text-neutral-300">
              <thead>
                <tr className="border-b border-neutral-800 text-[11px] font-mono uppercase text-neutral-400">
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Feature Name</th>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Requirement Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800/60">
                {prdData.functional_requirements.map((f) => (
                  <tr key={f.id} className="hover:bg-neutral-800/30">
                    <td className="py-3 px-4 font-mono font-bold text-indigo-400">{f.id}</td>
                    <td className="py-3 px-4 font-semibold text-white">{f.feature}</td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                        {f.priority}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-neutral-400">{f.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Non-Functional & Success Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Non-Functional */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <h3 className="font-bold text-sm text-white border-b border-neutral-800 pb-3">
                Non-Functional Requirements
              </h3>
              <div className="space-y-3 pt-1">
                {prdData.non_functional_requirements.map((n) => (
                  <div key={n.id} className="bg-neutral-950 border border-neutral-800/80 rounded-xl p-3 space-y-1">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-indigo-400 font-bold">{n.id} • {n.category}</span>
                    </div>
                    <p className="text-xs text-neutral-300">{n.target}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Success Metrics */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 border-b border-neutral-800 pb-3">
                <Target className="w-4 h-4 text-cyan-400" />
                <h3 className="font-bold text-sm text-white">Target Success KPIs</h3>
              </div>
              <div className="space-y-3 pt-1">
                {prdData.success_metrics.map((m, i) => (
                  <div key={i} className="flex items-center justify-between bg-neutral-950 border border-neutral-800/80 rounded-xl p-3.5">
                    <span className="text-xs font-medium text-neutral-300">{m.metric}</span>
                    <span className="text-xs font-mono font-bold text-cyan-400 bg-cyan-950/60 border border-cyan-800/50 px-2.5 py-1 rounded">
                      {m.target}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
