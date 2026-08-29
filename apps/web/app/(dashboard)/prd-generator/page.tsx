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
  ArrowRight,
  Shield,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

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
  const [selectedModel, setSelectedModel] = useState<string>(
    "llama-3.3-70b-versatile",
  );
  const [customInstructions, setCustomInstructions] = useState<string>("");
  const [prdData, setPrdData] = useState<PRDResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isCopied, setIsCopied] = useState<boolean>(false);

  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const fetchPRD = async (
    title?: string,
    category?: string,
    description?: string,
    instructions?: string,
  ) => {
    setIsLoading(true);
    try {
      const projTitle = title || activeProject?.title || "Startup Concept";
      const projCategory = category || activeProject?.category || "B2B SaaS";
      const baseProblem = description || activeProject?.description || "Founders lack rapid technical feasibility validation.";
      const problemStmt = instructions 
        ? `${baseProblem}. Additional focus: ${instructions}` 
        : baseProblem;

      const res = await api.post<PRDResponse>("/ai/prd", {
        title: projTitle,
        category: projCategory,
        problem_statement: problemStmt,
        solution_description:
          "Automated AI co-founder for technical architecture scoping, decision modeling, and execution.",
        target_users: "Startup Founders, Product Managers, Engineers, Investors",
        project_id: activeProjectId || undefined,
        provider: "groq",
        model: selectedModel,
      });
      setPrdData(res.data);
      toast.success("PRD generated successfully with AI!");
    } catch (err) {
      console.error("Failed to load PRD:", err);
      toast.error("Failed to generate PRD.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeProject) {
      fetchPRD(
        activeProject.title,
        activeProject.category || "B2B SaaS",
        activeProject.description || "",
      );
    } else if (projects.length === 0 && !projectsQuery.isLoading) {
      fetchPRD("Nexus AI", "B2B SaaS", "AI platform validation");
    }
  }, [activeProjectId]);

  const handleRegenerate = () => {
    fetchPRD(
      activeProject?.title || "Startup Concept",
      activeProject?.category || "B2B SaaS",
      activeProject?.description || "",
      customInstructions,
    );
  };

  const handleDownloadMarkdown = () => {
    if (!prdData) return;
    const md = `# ${prdData.title}
**Version**: ${prdData.version} | **Status**: ${prdData.status} | **Category**: ${prdData.category}  

---

## Executive Summary
${prdData.executive_summary}

---

## Problem Definition
- **Core Problem**: ${prdData.problem_definition?.core_problem || "N/A"}
- **Current Alternatives**: ${(prdData.problem_definition?.current_alternatives || []).join(", ")}
- **Why Now**: ${prdData.problem_definition?.why_now || "N/A"}

---

## User Personas
${(prdData.user_personas || []).map((p) => `### ${p.persona}\n${p.need}`).join("\n\n")}

---

## Functional Requirements
| ID | Feature | Priority | Description |
| :--- | :--- | :--- | :--- |
${(prdData.functional_requirements || []).map((f) => `| ${f.id} | ${f.feature} | ${f.priority} | ${f.description} |`).join("\n")}

---

## Non-Functional Requirements
| ID | Category | Target Metric |
| :--- | :--- | :--- |
${(prdData.non_functional_requirements || []).map((n) => `| ${n.id} | ${n.category} | ${n.target} |`).join("\n")}

---

## Success Metrics (KPIs)
${(prdData.success_metrics || []).map((m) => `- **${m.metric}**: ${m.target}`).join("\n")}
`;

    const blob = new Blob([md], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${(prdData.title || "prd").toLowerCase().replace(/[^a-z0-9]+/g, "-")}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("PRD Markdown downloaded!");
  };

  const handleCopy = () => {
    if (!prdData) return;
    navigator.clipboard.writeText(JSON.stringify(prdData, null, 2));
    setIsCopied(true);
    toast.success("Copied PRD JSON to clipboard!");
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
          <h1 className="text-3xl font-bold text-white tracking-tight">
            PRD Generator
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Automated Product Requirements Documents with user personas,
            functional specs, and success KPIs.
          </p>
        </div>

        {/* Project Selector & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedModel}
            onChange={(e) => {
              setSelectedModel(e.target.value);
            }}
            className="bg-neutral-900 border border-neutral-800 rounded-lg px-2.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            <option value="llama-3.3-70b-versatile">
              Llama 3.3 70B (Groq Fast)
            </option>
            <option value="llama-3.1-8b-instant">
              Llama 3.1 8B Instant (Ultra Fast)
            </option>
            <option value="qwen/qwen3.8-27b">Qwen 3.8 27B (Groq)</option>
            <option value="openai/gpt-oss-20b">GPT-OSS 20B (Groq)</option>
          </select>

          {projects.length > 0 && (
            <div className="flex items-center gap-2 bg-neutral-900 border border-neutral-800 rounded-lg p-2">
              <Layers className="w-4 h-4 text-neutral-400 ml-1" />
              <select
                value={activeProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                className="bg-transparent text-xs text-neutral-200 focus:outline-none cursor-pointer pr-2"
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

          {/* AI REGENERATE BUTTON */}
          <Button
            onClick={handleRegenerate}
            disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-all shadow-lg shadow-indigo-950/50"
          >
            {isLoading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>{isLoading ? "Regenerating..." : "Regenerate with AI"}</span>
          </Button>

          {prdData && (
            <Button
              variant="outline"
              onClick={handleDownloadMarkdown}
              className="inline-flex items-center gap-1.5 px-3.5 py-2 border-neutral-700 bg-neutral-900 hover:bg-neutral-800 text-white rounded-lg text-xs font-bold transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download MD</span>
            </Button>
          )}
        </div>
      </div>

      {/* Optional Refinement Bar */}
      <div className="bg-neutral-900/70 border border-neutral-800 rounded-xl p-3 flex flex-col sm:flex-row items-center gap-3">
        <div className="text-xs font-medium text-neutral-400 shrink-0 flex items-center gap-1.5 pl-2">
          <Zap className="w-3.5 h-3.5 text-indigo-400" />
          <span>Refinement Instruction:</span>
        </div>
        <input
          type="text"
          value={customInstructions}
          onChange={(e) => setCustomInstructions(e.target.value)}
          placeholder="e.g. Focus heavily on security, enterprise SSO, and mobile responsiveness..."
          className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-neutral-500 focus:outline-none focus:border-indigo-500"
          onKeyDown={(e) => {
            if (e.key === "Enter") handleRegenerate();
          }}
        />
        <Button
          onClick={handleRegenerate}
          disabled={isLoading}
          size="sm"
          variant="secondary"
          className="shrink-0 text-xs h-8 bg-neutral-800 hover:bg-neutral-700 text-white"
        >
          Apply &amp; Re-run
        </Button>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
          <span className="text-sm font-medium">Synthesizing Product Requirements Document with AI Gateway...</span>
          <span className="text-xs text-neutral-500">Generating user personas, functional specifications, and KPI targets</span>
        </div>
      ) : !prdData ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <FileText className="w-12 h-12 text-neutral-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">No PRD Available</h3>
          <p className="text-xs text-neutral-400">
            Click &quot;Regenerate with AI&quot; to synthesize product specifications.
          </p>
          <Button
            onClick={handleRegenerate}
            className="bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white"
          >
            <Sparkles className="w-3.5 h-3.5 mr-2" />
            Generate PRD Now
          </Button>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* PRD Meta Card */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-6 flex items-center gap-2">
              <span className="px-2.5 py-1 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-full text-xs font-bold">
                {prdData.status || "APPROVED"}
              </span>
              <span className="px-2.5 py-1 bg-neutral-800 border border-neutral-700 text-neutral-300 rounded-full text-xs font-mono">
                {prdData.version || "v1.0.0"}
              </span>
              <button
                onClick={handleCopy}
                className="p-1.5 bg-neutral-800 hover:bg-neutral-700 text-neutral-300 rounded-lg text-xs transition-colors ml-2"
                title="Copy JSON"
              >
                {isCopied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>

            <div className="space-y-3 max-w-2xl">
              <span className="text-[11px] font-bold uppercase tracking-wider text-indigo-400">
                {prdData.category}
              </span>
              <h2 className="text-2xl font-black text-white">
                {prdData.title}
              </h2>
              <p className="text-xs text-neutral-300 leading-relaxed font-sans">
                {prdData.executive_summary}
              </p>
            </div>
          </div>

          {/* Section 1: Problem Definition & Personas */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Problem Definition */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <Target className="w-4 h-4" />
                <span>Problem Definition</span>
              </div>

              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-neutral-500 font-semibold uppercase text-[10px]">
                    Core Problem
                  </span>
                  <p className="text-neutral-200 mt-1">
                    {prdData.problem_definition?.core_problem}
                  </p>
                </div>

                <div>
                  <span className="text-neutral-500 font-semibold uppercase text-[10px]">
                    Why Now?
                  </span>
                  <p className="text-neutral-200 mt-1">
                    {prdData.problem_definition?.why_now}
                  </p>
                </div>

                <div>
                  <span className="text-neutral-500 font-semibold uppercase text-[10px]">
                    Current Alternatives
                  </span>
                  <ul className="list-disc list-inside text-neutral-400 space-y-1 mt-1">
                    {(prdData.problem_definition?.current_alternatives || []).map(
                      (alt, idx) => (
                        <li key={idx}>{alt}</li>
                      ),
                    )}
                  </ul>
                </div>
              </div>
            </div>

            {/* Target Personas */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <Users className="w-4 h-4" />
                <span>Target User Personas</span>
              </div>

              <div className="space-y-3">
                {(prdData.user_personas || []).map((p, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-neutral-950 border border-neutral-800 rounded-xl space-y-1"
                  >
                    <span className="font-semibold text-xs text-white">
                      {p.persona}
                    </span>
                    <p className="text-xs text-neutral-400 leading-relaxed">
                      {p.need}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Section 2: Functional Requirements */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4 overflow-x-auto">
            <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
              <ListOrdered className="w-4 h-4" />
              <span>Functional Requirements Specification</span>
            </div>

            <table className="w-full text-left text-xs text-neutral-300">
              <thead>
                <tr className="border-b border-neutral-800 text-[11px] font-mono uppercase text-neutral-400">
                  <th className="py-3 px-4">ID</th>
                  <th className="py-3 px-4">Feature Name</th>
                  <th className="py-3 px-4">Priority</th>
                  <th className="py-3 px-4">Detailed Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-800/60 font-sans">
                {(prdData.functional_requirements || []).map((f, idx) => (
                  <tr key={idx} className="hover:bg-neutral-800/30">
                    <td className="py-3 px-4 font-mono text-neutral-400">
                      {f.id}
                    </td>
                    <td className="py-3 px-4 text-white font-semibold">
                      {f.feature}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded font-bold font-mono text-[10px] ${
                          f.priority === "P0"
                            ? "bg-red-500/10 text-red-400 border border-red-500/20"
                            : f.priority === "P1"
                              ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                        }`}
                      >
                        {f.priority}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-neutral-300 max-w-md">
                      {f.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Section 3: Non-Functional & Success Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Non-Functional Specs */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <Shield className="w-4 h-4" />
                <span>Non-Functional Quality Attributes</span>
              </div>

              <div className="space-y-2">
                {(prdData.non_functional_requirements || []).map((n, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-neutral-950 border border-neutral-800 rounded-xl flex items-center justify-between text-xs"
                  >
                    <span className="font-semibold text-neutral-300">
                      {n.category}
                    </span>
                    <span className="font-mono text-indigo-400">{n.target}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Success KPIs */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                <CheckCircle2 className="w-4 h-4" />
                <span>Success Metrics &amp; KPIs</span>
              </div>

              <div className="space-y-2">
                {(prdData.success_metrics || []).map((m, idx) => (
                  <div
                    key={idx}
                    className="p-3 bg-neutral-950 border border-neutral-800 rounded-xl flex items-center justify-between text-xs"
                  >
                    <span className="font-medium text-neutral-300">
                      {m.metric}
                    </span>
                    <span className="font-mono font-bold text-emerald-400">
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
