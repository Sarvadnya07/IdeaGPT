"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import {
  Layers,
  Sparkles,
  RefreshCw,
  Server,
  Database,
  Shield,
  Network,
  Code2,
  Lock,
  ArrowRight,
  CheckCircle2,
  DollarSign,
  Boxes,
  Zap,
} from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { MermaidViewer } from "@/components/execution/MermaidViewer";
import { CloudCostEstimator } from "@/components/execution/CloudCostEstimator";

interface ArchitectureBlueprintResponse {
  title: string;
  category: string;
  description: string;
  topology: Record<string, string>;
  mermaid_diagram: string;
  api_endpoints: Array<{
    method: string;
    path: string;
    description: string;
  }>;
  database_entities: Array<{
    table: string;
    columns: string[];
    description: string;
  }>;
  security_specifications: string[];
}

export default function ArchitecturePage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects({ limit: 50 });
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const [selectedModel, setSelectedModel] = useState<string>(
    "llama-3.3-70b-versatile",
  );
  const [activeTab, setActiveTab] = useState<
    "topology" | "apis" | "database" | "security" | "cloud_costs"
  >("topology");
  const [blueprint, setBlueprint] =
    useState<ArchitectureBlueprintResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [customTopologyFocus, setCustomTopologyFocus] = useState<string>("");

  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const fetchBlueprint = async (
    title?: string,
    category?: string,
    desc?: string,
    customFocus?: string,
  ) => {
    setIsLoading(true);
    try {
      const projTitle = title || activeProject?.title || "Startup Concept";
      const projCategory = category || activeProject?.category || "B2B SaaS";
      const baseDesc = desc || activeProject?.description || "Cloud-native scalable AI co-founder architecture.";
      const finalDesc = customFocus ? `${baseDesc}. Focus: ${customFocus}` : baseDesc;

      const res = await api.post<ArchitectureBlueprintResponse>(
        "/ai/architecture",
        {
          title: projTitle,
          category: projCategory,
          description: finalDesc,
          provider: "groq",
          model: selectedModel,
        },
      );
      setBlueprint(res.data);
      toast.success("Architecture Blueprint synthesized with AI!");
    } catch (err) {
      console.error("Failed to load blueprint:", err);
      toast.error("Failed to generate architecture blueprint.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (activeProject) {
      fetchBlueprint(
        activeProject.title,
        activeProject.category || "B2B SaaS",
        activeProject.description || "",
      );
    } else if (projects.length === 0 && !projectsQuery.isLoading) {
      fetchBlueprint(
        "IdeaGPT System",
        "B2B SaaS",
        "AI Co-Founder Architecture",
      );
    }
  }, [activeProjectId]);

  const handleRegenerate = () => {
    fetchBlueprint(
      activeProject?.title || "Startup Concept",
      activeProject?.category || "B2B SaaS",
      activeProject?.description || "",
      customTopologyFocus,
    );
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <Boxes className="w-4 h-4" />
            <span>Blueprint Studio &amp; Systems Engineering</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Blueprint Studio
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            System topology, interactive Mermaid diagrams, REST API specs, database entity schemas, and multi-cloud FinOps.
          </p>
        </div>

        {/* Project Selector & AI Actions */}
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
            <span>{isLoading ? "Regenerating..." : "Regenerate Blueprint with AI"}</span>
          </Button>
        </div>
      </div>

      {/* Refinement Prompt Bar */}
      <div className="bg-neutral-900/70 border border-neutral-800 rounded-xl p-3 flex flex-col sm:flex-row items-center gap-3">
        <div className="text-xs font-medium text-neutral-400 shrink-0 flex items-center gap-1.5 pl-2">
          <Zap className="w-3.5 h-3.5 text-indigo-400" />
          <span>Architecture Focus:</span>
        </div>
        <input
          type="text"
          value={customTopologyFocus}
          onChange={(e) => setCustomTopologyFocus(e.target.value)}
          placeholder="e.g. Microservices vs Modular Monolith, AWS ECS Fargate, pgvector embeddings..."
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
          Re-architect
        </Button>
      </div>

      {/* Main Content */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-6 h-6 animate-spin text-indigo-400" />
          <span className="text-sm font-medium">Synthesizing System Architecture Blueprint with AI Gateway...</span>
          <span className="text-xs text-neutral-500">Generating Mermaid data flow, database schemas, and REST endpoints</span>
        </div>
      ) : !blueprint ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <Network className="w-12 h-12 text-neutral-600 mx-auto" />
          <h3 className="text-lg font-bold text-white">
            No Architecture Blueprint Available
          </h3>
          <p className="text-xs text-neutral-400">
            Click &quot;Regenerate Blueprint with AI&quot; to synthesize system architecture models.
          </p>
          <Button
            onClick={handleRegenerate}
            className="bg-indigo-600 hover:bg-indigo-500 text-xs font-bold text-white"
          >
            <Sparkles className="w-3.5 h-3.5 mr-2" />
            Synthesize Blueprint Now
          </Button>
        </div>
      ) : (
        <div className="space-y-8 animate-in fade-in duration-300">
          {/* Navigation Tabs */}
          <div className="flex flex-wrap items-center gap-2 border-b border-neutral-800 pb-2">
            {[
              { id: "topology", label: "System Topology & Diagram", icon: Server },
              { id: "apis", label: "API Endpoints", icon: Code2 },
              { id: "database", label: "Database Entities", icon: Database },
              { id: "security", label: "Security & Isolation", icon: Shield },
              { id: "cloud_costs", label: "Cloud Cost Estimator", icon: DollarSign },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-neutral-400 hover:text-white hover:bg-neutral-900"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* TAB 1: System Topology & Live Mermaid Diagram */}
          {activeTab === "topology" && (
            <div className="space-y-6">
              {/* Topology Layers Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(blueprint.topology || {}).map(([layerKey, val]) => (
                  <div
                    key={layerKey}
                    className="bg-neutral-900/80 border border-neutral-800 rounded-xl p-4 space-y-1.5"
                  >
                    <span className="text-[10px] font-mono uppercase text-indigo-400 font-bold tracking-wider">
                      {layerKey.replace(/_/g, " ")}
                    </span>
                    <div className="font-semibold text-xs text-white">
                      {val}
                    </div>
                  </div>
                ))}
              </div>

              {/* Live Interactive Mermaid Diagram Component */}
              <MermaidViewer
                chart={blueprint.mermaid_diagram || "graph TD; Client-->APIGateway; APIGateway-->Database;"}
                title={`${blueprint.title || "System"} Architectural Data Flow`}
              />
            </div>
          )}

          {/* TAB 2: API Specifications */}
          {activeTab === "apis" && (
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4 overflow-x-auto">
              <h3 className="text-base font-bold text-white border-b border-neutral-800 pb-3">
                RESTful API Endpoint Registry
              </h3>

              <table className="w-full text-left text-xs text-neutral-300">
                <thead>
                  <tr className="border-b border-neutral-800 text-[11px] font-mono uppercase text-neutral-400">
                    <th className="py-3 px-4">Method</th>
                    <th className="py-3 px-4">Endpoint Route</th>
                    <th className="py-3 px-4">Functionality</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-neutral-800/60 font-mono">
                  {(blueprint.api_endpoints || []).map((ep, idx) => (
                    <tr key={idx} className="hover:bg-neutral-800/30">
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded font-bold text-[10px] ${
                            ep.method === "GET"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : ep.method === "POST"
                                ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                                : ep.method === "PATCH"
                                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                                  : "bg-red-500/10 text-red-400 border border-red-500/20"
                          }`}
                        >
                          {ep.method}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-white font-semibold">
                        {ep.path}
                      </td>
                      <td className="py-3 px-4 text-neutral-400 font-sans">
                        {ep.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* TAB 3: Database Entity Models */}
          {activeTab === "database" && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {(blueprint.database_entities || []).map((tbl, i) => (
                <div
                  key={i}
                  className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-3"
                >
                  <div className="flex items-center gap-2 border-b border-neutral-800 pb-2">
                    <Database className="w-4 h-4 text-amber-400" />
                    <h4 className="font-mono font-bold text-sm text-white">
                      {tbl.table}
                    </h4>
                  </div>
                  <p className="text-xs text-neutral-400 leading-relaxed">
                    {tbl.description}
                  </p>
                  <div className="space-y-1 pt-1">
                    <span className="text-[10px] uppercase font-mono text-neutral-500">
                      Columns:
                    </span>
                    <ul className="space-y-0.5 text-xs font-mono text-neutral-300">
                      {(tbl.columns || []).map((col, cIdx) => (
                        <li key={cIdx} className="text-neutral-400 text-[11px]">
                          • {col}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* TAB 4: Security & Isolation */}
          {activeTab === "security" && (
            <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 space-y-4">
              <h3 className="text-base font-bold text-white border-b border-neutral-800 pb-3 flex items-center gap-2">
                <Lock className="w-4 h-4 text-cyan-400" />
                <span>Security Controls &amp; Multi-Tenant Boundary</span>
              </h3>

              <div className="space-y-3 pt-2">
                {(blueprint.security_specifications || []).map((sec, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 bg-neutral-950 border border-neutral-800/80 p-3.5 rounded-xl"
                  >
                    <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                    <span className="text-xs text-neutral-300 leading-relaxed">
                      {sec}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 5: Cloud Cost Estimator */}
          {activeTab === "cloud_costs" && (
            <div className="space-y-6">
              <CloudCostEstimator />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
