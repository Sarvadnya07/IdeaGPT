"use client";

import React, { useState } from "react";
import {
  Cpu,
  Search,
  CheckCircle,
  AlertTriangle,
  Play,
  ArrowRight,
  TrendingUp,
  Activity,
  GitPullRequest,
  GitMerge,
  GitBranch,
} from "lucide-react";
import { toast } from "sonner";

export default function GitHubLabPage() {
  const [repoName, setRepoName] = useState("facebook/react");
  const [loading, setLoading] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoName) return;
    setLoading(true);
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 1500)),
      {
        loading: `Cloning & analyzing ${repoName} in sandboxed runtime...`,
        success: () => {
          setLoading(false);
          return `${repoName} intelligence indices successfully updated!`;
        },
        error: "Failed to analyze repository",
      }
    );
  };

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Header bar with search input */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            AI DevOps & Sandboxes
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            GitHub Intelligence Lab
          </h1>
        </div>

        <form onSubmit={handleSearch} className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            value={repoName}
            onChange={(e) => setRepoName(e.target.value)}
            placeholder="Search repositories..."
            className="block w-full pl-9 pr-12 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-650"
          />
          <button
            type="submit"
            className="absolute right-2 top-1.5 text-[9px] font-bold text-indigo-400 hover:text-indigo-300 uppercase tracking-wider"
          >
            Analyze
          </button>
        </form>
      </div>

      {/* Repository Card Panel */}
      <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-indigo-500/5 blur-[80px] pointer-events-none"></div>

        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[8px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-400 uppercase tracking-wider">
              Public
            </span>
            <span className="text-xs font-semibold text-zinc-500 flex items-center gap-1">
              <GitBranch className="w-3.5 h-3.5 text-zinc-600" />
              main
            </span>
          </div>

          <h2 className="text-2xl font-black text-white leading-snug tracking-tight">
            {repoName}
          </h2>
          <p className="text-xs text-zinc-500 max-w-xl leading-relaxed font-medium">
            {repoName === "facebook/react"
              ? "A declarative, efficient, and flexible JavaScript library for building user interfaces."
              : "Repository analyzed inside IdeaGPT AI Engine. Technical capability metrics successfully indexed."}
          </p>
        </div>
      </div>

      {/* Grid Content metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* KPI 1: Code Volume */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[160px] relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              Commits Evaluated
            </span>
            <span className="w-6 h-6 rounded-md bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <Activity className="w-3.5 h-3.5" />
            </span>
          </div>

          <div className="my-2">
            <div className="text-3xl font-black text-white tracking-tight">18.4k</div>
            <div className="flex items-center gap-1 text-[9px] font-bold text-emerald-400 mt-1">
              <TrendingUp className="w-3 h-3" />
              99.8% code test coverage
            </div>
          </div>
        </div>

        {/* KPI 2: Code Quality */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[160px] relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              PRs Merged
            </span>
            <span className="w-6 h-6 rounded-md bg-purple-500/10 flex items-center justify-center text-purple-400">
              <GitMerge className="w-3.5 h-3.5" />
            </span>
          </div>

          <div className="my-2">
            <div className="text-3xl font-black text-white tracking-tight">12.5k</div>
            <div className="flex items-center gap-1 text-[9px] font-bold text-emerald-400 mt-1">
              <TrendingUp className="w-3 h-3" />
              Avg 1.5h review latency
            </div>
          </div>
        </div>

        {/* KPI 3: Issues Blockers */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[160px] relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              Active Issues
            </span>
            <span className="w-6 h-6 rounded-md bg-red-500/10 flex items-center justify-center text-red-400">
              <GitPullRequest className="w-3.5 h-3.5" />
            </span>
          </div>

          <div className="my-2">
            <div className="text-3xl font-black text-white tracking-tight">412</div>
            <div className="flex items-center gap-1 text-[9px] font-bold text-zinc-500 mt-1">
              <CheckCircle className="w-3 h-3 text-zinc-500" />
              0 blocker priority issues
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
