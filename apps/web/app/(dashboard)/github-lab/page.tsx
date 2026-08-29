"use client";

import React, { useState } from "react";
import { useProjects } from "../../../hooks/useProjects";
import { useApiClient } from "@/lib/api/client";
import { toast } from "sonner";
import {
  GitBranch,
  FolderTree,
  FileCode,
  Terminal,
  Copy,
  Check,
  Loader2,
  RefreshCw,
  ExternalLink,
  BookOpen,
  Box,
  Layers,
} from "lucide-react";

interface DirectoryItem {
  path: string;
  type: "file" | "dir";
  description: string;
}

interface OpenSourceLib {
  name: string;
  purpose: string;
  url: string;
}

interface GitHubLabResult {
  repository_name: string;
  description: string;
  license: string;
  directory_tree: DirectoryItem[];
  ci_cd_workflow: string;
  dockerfile: string;
  readme_content: string;
  recommended_open_source_libs: OpenSourceLib[];
}

export default function GithubLabPage() {
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];

  const [selectedProjectId, setSelectedProjectId] = useState<string>("");
  const activeProjectId =
    selectedProjectId || (projects.length > 0 ? projects[0].id : "");
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const [isGenerating, setIsGenerating] = useState(false);
  const [result, setResult] = useState<GitHubLabResult | null>(null);
  const [activeTab, setActiveTab] = useState<
    "tree" | "cicd" | "docker" | "readme"
  >("tree");
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!activeProject) {
      toast.error("Please select a project first.");
      return;
    }
    setIsGenerating(true);
    try {
      const res = await api.post<GitHubLabResult>("/ai/labs/github", {
        title: activeProject.title,
        category: activeProject.category || "B2B SaaS",
        description: activeProject.description || "",
      });
      setResult(res.data);
      toast.success("GitHub Codebase Scaffolding generated successfully!");
    } catch (err: any) {
      toast.error("Failed to generate repository blueprint");
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    toast.success("Copied to clipboard!");
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="space-y-8 py-4 max-w-6xl mx-auto">
      {/* Top Banner Heading */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-zinc-900 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-zinc-800 text-zinc-300 border border-zinc-700 uppercase tracking-widest gap-1.5">
              <GitBranch className="w-3 h-3" /> GitHub Architecture Lab
            </span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {activeProject?.title || "Codebase Scaffolder"}
          </h1>
          <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
            Generate production repository directory structures, CI/CD automated
            test workflows, Docker container definitions, and comprehensive
            README documentation.
          </p>
        </div>

        {/* Project Selector & Actions */}
        <div className="flex items-center gap-3 shrink-0">
          <select
            value={activeProjectId}
            onChange={(e) => setSelectedProjectId(e.target.value)}
            className="bg-[#0b0b0d] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
          >
            {projects.map((p) => (
              <option key={p.id} value={p.id}>
                {p.title}
              </option>
            ))}
          </select>
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !activeProject}
            className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-bold transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)] cursor-pointer"
          >
            {isGenerating ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" /> Synthesizing
                Repo...
              </>
            ) : (
              <>
                <RefreshCw className="w-3.5 h-3.5" /> Scaffold Codebase
              </>
            )}
          </button>
        </div>
      </div>

      {result ? (
        <div className="space-y-6">
          {/* Repo Overview Card */}
          <div className="p-6 rounded-2xl bg-zinc-950/60 border border-zinc-900 flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-2">
                <Box className="w-5 h-5 text-indigo-400" />
                <h3 className="text-lg font-bold text-white font-mono">
                  {result.repository_name}
                </h3>
                <span className="px-2 py-0.5 text-[10px] font-mono bg-zinc-800 text-zinc-400 rounded-md">
                  {result.license} License
                </span>
              </div>
              <p className="text-xs text-zinc-400 mt-1">{result.description}</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() =>
                  copyToClipboard(result.readme_content, "readme_full")
                }
                className="px-3 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 rounded-xl text-xs font-medium border border-zinc-800 flex items-center gap-1.5"
              >
                {copiedKey === "readme_full" ? (
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Copy className="w-3.5 h-3.5" />
                )}
                Copy README
              </button>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex border-b border-zinc-900 gap-2">
            <button
              onClick={() => setActiveTab("tree")}
              className={`px-4 py-2 text-xs font-semibold rounded-t-xl transition-all flex items-center gap-2 ${
                activeTab === "tree"
                  ? "bg-zinc-900/80 text-white border-t border-x border-zinc-800"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <FolderTree className="w-3.5 h-3.5" /> Directory Structure
            </button>
            <button
              onClick={() => setActiveTab("cicd")}
              className={`px-4 py-2 text-xs font-semibold rounded-t-xl transition-all flex items-center gap-2 ${
                activeTab === "cicd"
                  ? "bg-zinc-900/80 text-white border-t border-x border-zinc-800"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <FileCode className="w-3.5 h-3.5" /> CI/CD Workflow (.yml)
            </button>
            <button
              onClick={() => setActiveTab("docker")}
              className={`px-4 py-2 text-xs font-semibold rounded-t-xl transition-all flex items-center gap-2 ${
                activeTab === "docker"
                  ? "bg-zinc-900/80 text-white border-t border-x border-zinc-800"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <Terminal className="w-3.5 h-3.5" /> Dockerfile
            </button>
            <button
              onClick={() => setActiveTab("readme")}
              className={`px-4 py-2 text-xs font-semibold rounded-t-xl transition-all flex items-center gap-2 ${
                activeTab === "readme"
                  ? "bg-zinc-900/80 text-white border-t border-x border-zinc-800"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" /> README Preview
            </button>
          </div>

          {/* Tab Content Panes */}
          <div className="p-6 rounded-2xl bg-[#0b0b0d] border border-zinc-900">
            {activeTab === "tree" && (
              <div className="space-y-3">
                <span className="text-xs font-bold text-zinc-400 uppercase tracking-wider block mb-4">
                  Target Repository Tree Layout
                </span>
                <div className="space-y-2">
                  {result.directory_tree.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 rounded-xl bg-zinc-950/60 border border-zinc-900 text-xs"
                    >
                      <div className="flex items-center gap-3 font-mono">
                        {item.type === "dir" ? (
                          <span className="text-amber-400">
                            📁 {item.path}/
                          </span>
                        ) : (
                          <span className="text-indigo-400">
                            📄 {item.path}
                          </span>
                        )}
                      </div>
                      <span className="text-zinc-500 text-[11px]">
                        {item.description}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {activeTab === "cicd" && (
              <div className="space-y-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-mono text-zinc-400">
                    .github/workflows/ci.yml
                  </span>
                  <button
                    onClick={() =>
                      copyToClipboard(result.ci_cd_workflow, "cicd")
                    }
                    className="p-1.5 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 rounded-lg text-xs flex items-center gap-1"
                  >
                    {copiedKey === "cicd" ? (
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
                <pre className="p-4 rounded-xl bg-black/70 border border-zinc-900 text-emerald-400 font-mono text-xs overflow-x-auto">
                  {result.ci_cd_workflow}
                </pre>
              </div>
            )}

            {activeTab === "docker" && (
              <div className="space-y-3">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-mono text-zinc-400">
                    Dockerfile
                  </span>
                  <button
                    onClick={() => copyToClipboard(result.dockerfile, "docker")}
                    className="p-1.5 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 rounded-lg text-xs flex items-center gap-1"
                  >
                    {copiedKey === "docker" ? (
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
                <pre className="p-4 rounded-xl bg-black/70 border border-zinc-900 text-cyan-400 font-mono text-xs overflow-x-auto">
                  {result.dockerfile}
                </pre>
              </div>
            )}

            {activeTab === "readme" && (
              <div className="space-y-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-mono text-zinc-400">
                    README.md
                  </span>
                  <button
                    onClick={() =>
                      copyToClipboard(result.readme_content, "readme_tab")
                    }
                    className="p-1.5 bg-zinc-900 hover:bg-zinc-800 text-zinc-300 rounded-lg text-xs flex items-center gap-1"
                  >
                    {copiedKey === "readme_tab" ? (
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                    ) : (
                      <Copy className="w-3.5 h-3.5" />
                    )}
                  </button>
                </div>
                <div className="p-6 rounded-xl bg-black/50 border border-zinc-900 text-zinc-300 text-xs whitespace-pre-wrap font-sans leading-relaxed">
                  {result.readme_content}
                </div>
              </div>
            )}
          </div>

          {/* Open Source Recommended Dependencies */}
          {result.recommended_open_source_libs?.length > 0 && (
            <div className="p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900">
              <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-wider mb-4 flex items-center gap-2">
                <Layers className="w-4 h-4 text-indigo-400" /> Recommended
                High-Leverage Open Source Stack
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {result.recommended_open_source_libs.map((lib, idx) => (
                  <a
                    key={idx}
                    href={lib.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-3 rounded-xl bg-zinc-900/60 border border-zinc-800/80 hover:border-indigo-500/50 transition-all flex items-center justify-between text-xs group"
                  >
                    <div>
                      <span className="font-semibold text-white font-mono group-hover:text-indigo-300">
                        {lib.name}
                      </span>
                      <span className="text-zinc-500 block text-[11px] mt-0.5">
                        {lib.purpose}
                      </span>
                    </div>
                    <ExternalLink className="w-3.5 h-3.5 text-zinc-500 group-hover:text-indigo-400" />
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Empty State */
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <GitBranch className="w-12 h-12 text-zinc-700 mb-2" />
          <h3 className="text-lg font-bold text-white">
            No GitHub Codebase Generated Yet
          </h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            Click &quot;Scaffold Codebase&quot; above to synthesize complete
            directory layouts, GitHub Actions workflows, and deployment
            Dockerfiles.
          </p>
        </div>
      )}
    </div>
  );
}
