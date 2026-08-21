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
  Code2
} from "lucide-react";
import { toast } from "sonner";

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
  const [focus, setFocus] = useState<string>("balanced");
  const [techStackData, setTechStackData] = useState<TechStackResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Active project ID
  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const fetchTechStack = async (projTitle: string, projCategory: string, focusVal: string) => {
    setIsLoading(true);
    try {
      const res = await api.post<TechStackResponse>("/ai/tech-stack", {
        title: projTitle || "Startup Concept",
        category: projCategory || "B2B SaaS",
        focus: focusVal,
      });
      setTechStackData(res.data);
    } catch (err) {
      console.error("Failed to load tech stack:", err);
      toast.error("Failed to generate tech stack recommendation.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeProject) {
      fetchTechStack(activeProject.title, activeProject.category || "B2B SaaS", focus);
    } else if (projects.length === 0 && !projectsQuery.isLoading) {
      fetchTechStack("Nexus AI", "B2B SaaS", focus);
    }
  }, [activeProjectId, focus]);

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <Cpu className="w-4 h-4" />
            <span>AI Architecture & Stack Recommendations</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Tech Stack Architect</h1>
          <p className="text-neutral-400 text-sm mt-1">
            Deterministic technology stack specifications and trade-off matrices tailored to your project.
          </p>
        </div>

        {/* Project Selector & Strategy */}
        <div className="flex flex-wrap items-center gap-3">
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

          {/* Focus Toggle */}
          <div className="flex items-center bg-neutral-900 border border-neutral-800 rounded-lg p-1 text-xs">
            {["balanced", "rapid_mvp", "high_scale", "cost_optimized"].map((mode) => (
              <button
                key={mode}
                onClick={() => setFocus(mode)}
                className={`px-3 py-1 rounded-md capitalize transition-colors ${
                  focus === mode ? "bg-indigo-600 text-white font-semibold" : "text-neutral-400 hover:text-white"
                }`}
              >
                {mode.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Generating custom stack architecture...</span>
        </div>
      ) : !techStackData ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <Cpu className="w-12 h-12 text-neutral-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">No Stack Blueprint Available</h3>
          <p className="text-xs text-neutral-400">Select a project to generate custom recommendations.</p>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Blueprint Overview Banner */}
          <div className="bg-gradient-to-r from-indigo-950/60 via-neutral-900 to-neutral-900 border border-indigo-800/40 rounded-2xl p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div>
              <span className="text-[10px] font-mono font-bold uppercase tracking-widest text-indigo-400">
                Recommended Architecture Profile
              </span>
              <h2 className="text-2xl font-bold text-white mt-1">
                {techStackData.title} — {techStackData.category}
              </h2>
              <p className="text-xs text-neutral-400 mt-1">
                Optimized for <strong className="text-indigo-300 capitalize">{focus.replace("_", " ")}</strong> development lifecycle and enterprise resilience.
              </p>
            </div>

            <Link
              href="/architecture"
              className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl text-xs font-bold transition-colors shadow-lg shadow-indigo-950/50"
            >
              <span>View System Topology</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {/* 5-Layer Stack Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Layer 1: Frontend */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3 border-b border-neutral-800 pb-3">
                <Code2 className="w-5 h-5 text-indigo-400" />
                <h3 className="font-bold text-sm text-white">Frontend Architecture</h3>
              </div>
              <div className="space-y-3 text-xs">
                {Object.entries(techStackData.frontend).map(([k, v]) => (
                  <div key={k} className="space-y-0.5">
                    <span className="text-neutral-500 font-mono capitalize">{k.replace("_", " ")}:</span>
                    <div className="font-semibold text-neutral-200">{v}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Layer 2: Backend */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3 border-b border-neutral-800 pb-3">
                <Server className="w-5 h-5 text-emerald-400" />
                <h3 className="font-bold text-sm text-white">Backend & APIs</h3>
              </div>
              <div className="space-y-3 text-xs">
                {Object.entries(techStackData.backend).map(([k, v]) => (
                  <div key={k} className="space-y-0.5">
                    <span className="text-neutral-500 font-mono capitalize">{k.replace("_", " ")}:</span>
                    <div className="font-semibold text-neutral-200">{v}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Layer 3: Database & Caching */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3 border-b border-neutral-800 pb-3">
                <Database className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold text-sm text-white">Database & Persistence</h3>
              </div>
              <div className="space-y-3 text-xs">
                {Object.entries(techStackData.database_and_caching).map(([k, v]) => (
                  <div key={k} className="space-y-0.5">
                    <span className="text-neutral-500 font-mono capitalize">{k.replace("_", " ")}:</span>
                    <div className="font-semibold text-neutral-200">{v}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Layer 4: AI & ML Engine */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
              <div className="flex items-center gap-3 border-b border-neutral-800 pb-3">
                <Bot className="w-5 h-5 text-purple-400" />
                <h3 className="font-bold text-sm text-white">AI & ML Orchestration</h3>
              </div>
              <div className="space-y-3 text-xs">
                {Object.entries(techStackData.ai_and_ml).map(([k, v]) => (
                  <div key={k} className="space-y-0.5">
                    <span className="text-neutral-500 font-mono capitalize">{k.replace("_", " ")}:</span>
                    <div className="font-semibold text-neutral-200">{v}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Layer 5: DevOps & Security */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4 md:col-span-2 lg:col-span-2">
              <div className="flex items-center gap-3 border-b border-neutral-800 pb-3">
                <ShieldCheck className="w-5 h-5 text-cyan-400" />
                <h3 className="font-bold text-sm text-white">DevOps, Auth & Cloud Infrastructure</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                {Object.entries(techStackData.devops_and_security).map(([k, v]) => (
                  <div key={k} className="space-y-0.5">
                    <span className="text-neutral-500 font-mono capitalize">{k.replace("_", " ")}:</span>
                    <div className="font-semibold text-neutral-200">{v}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Architectural Trade-Offs Matrix */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
            <h3 className="text-base font-bold text-white border-b border-neutral-800 pb-3">
              Architectural Decisions & Trade-Offs
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5 pt-2">
              {techStackData.architectural_tradeoffs.map((item, i) => (
                <div key={i} className="bg-neutral-950 border border-neutral-800/80 rounded-xl p-4 space-y-3">
                  <div className="font-bold text-xs text-indigo-300">{item.decision}</div>
                  <div className="space-y-2 text-xs">
                    <div className="text-emerald-400">
                      <span className="font-semibold">Pros:</span> {item.pros}
                    </div>
                    <div className="text-amber-400/90">
                      <span className="font-semibold">Cons:</span> {item.cons}
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
