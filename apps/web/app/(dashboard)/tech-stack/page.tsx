"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import {
  Cpu,
  Layers,
  Sparkles,
  RefreshCw,
  Plus,
  Server,
  Database,
  ShieldCheck,
  Bot,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Code2,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";

interface TechStackResponse {
  title: string;
  category: string;
  focus: string;
  frontend: Record<string, string>;
  backend: Record<string, string>;
  database_and_caching: Record<string, string>;
  ai_and_ml: Record<string, string>;
  devops_and_security: Record<string, string>;
  architectural_tradeoffs: Array<{
    decision: string;
    pros: string;
    cons: string;
  }>;
}

export default function TechStackPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects({ limit: 50 });
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>(
    "llama-3.3-70b-versatile",
  );
  const [focus, setFocus] = useState<string>("balanced");
  const [techStackData, setTechStackData] = useState<TechStackResponse | null>(
    null,
  );
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Active project ID
  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const fetchTechStack = async (
    projTitle?: string,
    projCategory?: string,
    focusVal?: string,
  ) => {
    setIsLoading(true);
    try {
      const res = await api.post<TechStackResponse>("/ai/tech-stack", {
        title: projTitle || activeProject?.title || "Startup Concept",
        category: projCategory || activeProject?.category || "B2B SaaS",
        focus: focusVal || focus,
        project_id: activeProjectId || undefined,
        provider: "groq",
        model: selectedModel,
      });
      setTechStackData(res.data);
      toast.success("Tech Stack generated with AI!");
    } catch (err) {
      console.error("Failed to load tech stack:", err);
      toast.error("Failed to generate tech stack recommendation.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeProject) {
      fetchTechStack(
        activeProject.title,
        activeProject.category || "B2B SaaS",
        focus,
      );
    } else if (projects.length === 0 && !projectsQuery.isLoading) {
      fetchTechStack("Nexus AI", "B2B SaaS", focus);
    }
  }, [activeProjectId, focus]);

  const handleRegenerate = () => {
    fetchTechStack(
      activeProject?.title || "Startup Concept",
      activeProject?.category || "B2B SaaS",
      focus,
    );
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <Cpu className="w-4 h-4" />
            <span>Engineering Architecture &amp; Tooling</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Tech Stack Advisor
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Context-aware framework and infrastructure selection based on
            scalability, speed, and cost.
          </p>
        </div>

        {/* Project Selector & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
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
            <span>{isLoading ? "Regenerating..." : "Regenerate Stack with AI"}</span>
          </Button>

          {/* Focus Toggle */}
          <div className="flex items-center bg-neutral-900 border border-neutral-800 rounded-lg p-1 text-xs">
            {["balanced", "rapid_mvp", "high_scale", "cost_optimized"].map(
              (mode) => (
                <button
                  key={mode}
                  onClick={() => setFocus(mode)}
                  className={`px-3 py-1 rounded-md capitalize transition-colors ${
                    focus === mode
                      ? "bg-indigo-600 text-white font-semibold"
                      : "text-neutral-400 hover:text-white"
                  }`}
                >
                  {mode.replace("_", " ")}
                </button>
              ),
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
          <span className="text-sm font-medium">Recommending Optimal Production Tech Stack with AI Gateway...</span>
          <span className="text-xs text-neutral-500">Evaluating frameworks, database, AI gateways, and CI/CD tools</span>
        </div>
      ) : !techStackData ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <Cpu className="w-12 h-12 text-neutral-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">
            No Stack Blueprint Available
          </h3>
          <p className="text-xs text-neutral-400">
            Select a project or click &quot;Regenerate Stack with AI&quot;.
          </p>
          <Button
            onClick={handleRegenerate}
            className="bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white"
          >
            <Sparkles className="w-3.5 h-3.5 mr-2" />
            Generate Stack Blueprint
          </Button>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Blueprint Overview Banner */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                Recommended Topology for {techStackData.category}
              </span>
              <h2 className="text-2xl font-black text-white mt-1">
                {techStackData.title}
              </h2>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 rounded-full text-xs font-mono font-bold uppercase">
                Focus: {techStackData.focus.replace("_", " ")}
              </span>
            </div>
          </div>

          {/* Technology Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Frontend */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <Code2 className="w-4 h-4" />
                <span>Frontend Layer</span>
              </div>
              <div className="space-y-3">
                {Object.entries(techStackData.frontend || {}).map(([key, val]) => (
                  <div key={key} className="space-y-1">
                    <span className="text-[10px] uppercase font-mono text-neutral-500 font-semibold">
                      {key.replace(/_/g, " ")}
                    </span>
                    <p className="text-xs text-neutral-200 font-medium">{val}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Backend */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <Server className="w-4 h-4" />
                <span>Backend &amp; API Layer</span>
              </div>
              <div className="space-y-3">
                {Object.entries(techStackData.backend || {}).map(([key, val]) => (
                  <div key={key} className="space-y-1">
                    <span className="text-[10px] uppercase font-mono text-neutral-500 font-semibold">
                      {key.replace(/_/g, " ")}
                    </span>
                    <p className="text-xs text-neutral-200 font-medium">{val}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Database & Caching */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <Database className="w-4 h-4" />
                <span>Database &amp; Caching</span>
              </div>
              <div className="space-y-3">
                {Object.entries(techStackData.database_and_caching || {}).map(
                  ([key, val]) => (
                    <div key={key} className="space-y-1">
                      <span className="text-[10px] uppercase font-mono text-neutral-500 font-semibold">
                        {key.replace(/_/g, " ")}
                      </span>
                      <p className="text-xs text-neutral-200 font-medium">{val}</p>
                    </div>
                  ),
                )}
              </div>
            </div>

            {/* AI & ML */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <Bot className="w-4 h-4" />
                <span>AI &amp; Inference Pipeline</span>
              </div>
              <div className="space-y-3">
                {Object.entries(techStackData.ai_and_ml || {}).map(([key, val]) => (
                  <div key={key} className="space-y-1">
                    <span className="text-[10px] uppercase font-mono text-neutral-500 font-semibold">
                      {key.replace(/_/g, " ")}
                    </span>
                    <p className="text-xs text-neutral-200 font-medium">{val}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* DevOps & Security */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-indigo-400 font-bold text-sm">
                <ShieldCheck className="w-4 h-4" />
                <span>DevOps &amp; Security</span>
              </div>
              <div className="space-y-3">
                {Object.entries(techStackData.devops_and_security || {}).map(
                  ([key, val]) => (
                    <div key={key} className="space-y-1">
                      <span className="text-[10px] uppercase font-mono text-neutral-500 font-semibold">
                        {key.replace(/_/g, " ")}
                      </span>
                      <p className="text-xs text-neutral-200 font-medium">{val}</p>
                    </div>
                  ),
                )}
              </div>
            </div>
          </div>

          {/* Architectural Trade-offs Table */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-bold text-white border-b border-neutral-800 pb-3">
              Architectural Trade-Off Analysis
            </h3>
            <div className="space-y-3">
              {(techStackData.architectural_tradeoffs || []).map((tradeoff, idx) => (
                <div
                  key={idx}
                  className="p-4 bg-neutral-950 border border-neutral-800/80 rounded-xl space-y-2"
                >
                  <h4 className="font-semibold text-xs text-white">
                    {tradeoff.decision}
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                    <div className="flex items-start gap-2 text-emerald-400">
                      <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5" />
                      <span className="text-neutral-300">
                        <strong className="text-emerald-400 font-medium">
                          Pros:
                        </strong>{" "}
                        {tradeoff.pros}
                      </span>
                    </div>
                    <div className="flex items-start gap-2 text-amber-400">
                      <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                      <span className="text-neutral-300">
                        <strong className="text-amber-400 font-medium">
                          Cons:
                        </strong>{" "}
                        {tradeoff.cons}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
