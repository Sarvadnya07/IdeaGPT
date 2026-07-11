"use client";

import React from "react";
import { useIdea } from "../../providers";
import {
  TrendingUp,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  Sparkles,
  ArrowRight,
  MoreHorizontal,
  ChevronRight,
} from "lucide-react";

export default function AIAnalysisPage() {
  const { idea } = useIdea();

  // Tech stack rendering mapping
  const getTechStack = () => {
    if (idea.industry === "DeFi / Web3") {
      return [
        { name: "Next.js", bg: "bg-zinc-900 border-zinc-800 text-zinc-100", label: "N" },
        { name: "Tailwind CSS", bg: "bg-teal-500/10 border-teal-500/20 text-teal-300", label: "T" },
        { name: "Supabase", bg: "bg-emerald-500/10 border-emerald-500/20 text-emerald-300", label: "S" },
        { name: "Pinecone DB", bg: "bg-purple-500/10 border-purple-500/20 text-purple-300", label: "P" },
        { name: "Rust (Core)", bg: "bg-orange-500/10 border-orange-500/20 text-orange-400", label: "R" },
      ];
    }
    return [
      { name: "Next.js", bg: "bg-zinc-900 border-zinc-800 text-zinc-100", label: "N" },
      { name: "Tailwind CSS", bg: "bg-teal-500/10 border-teal-500/20 text-teal-300", label: "T" },
      { name: "FastAPI (Python)", bg: "bg-sky-500/10 border-sky-500/20 text-sky-300", label: "F" },
      { name: "PostgreSQL", bg: "bg-blue-500/10 border-blue-500/20 text-blue-300", label: "P" },
      { name: "OpenAI API", bg: "bg-green-500/10 border-green-500/20 text-green-300", label: "O" },
    ];
  };

  const techStack = getTechStack();

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Banner Heading */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase tracking-widest">
              Analysis Complete
            </span>
            <span className="text-xs font-semibold text-zinc-500">
              Project: {idea.title}
            </span>
          </div>
          <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">
            {idea.title}
          </h1>
          <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
            {idea.problem}
          </p>
        </div>

        {/* Dynamic Startup Potential Radial gauge */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 w-full md:w-[260px] flex items-center justify-between shrink-0 shadow-[0_4px_20px_rgba(0,0,0,0.35)] relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-[80px] h-[80px] bg-indigo-500/5 blur-[30px] pointer-events-none"></div>
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
              Startup Potential
            </span>
            <div className="text-xs font-bold text-zinc-300 mt-1">
              Top 12% of analyzed ideas.
            </div>
          </div>
          <div className="relative flex items-center justify-center shrink-0 w-16 h-16 ml-3">
            {/* SVG Circular Progress path */}
            <svg className="w-16 h-16 transform -rotate-90">
              <circle
                cx="32"
                cy="32"
                r="28"
                className="stroke-zinc-800/80"
                strokeWidth="4"
                fill="transparent"
              />
              <circle
                cx="32"
                cy="32"
                r="28"
                className="stroke-indigo-500 shadow-[0_0_12px_rgba(99,102,241,0.5)]"
                strokeWidth="4"
                fill="transparent"
                strokeDasharray={175}
                strokeDashoffset={175 - (175 * idea.potential) / 100}
                strokeLinecap="round"
              />
            </svg>
            <div className="absolute text-center">
              <span className="text-lg font-extrabold text-white leading-none">
                {idea.potential}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Grid Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Execution Analysis Card */}
        <div className="lg:col-span-2 bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] relative overflow-hidden flex flex-col justify-between min-h-[220px]">
          <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-indigo-500/5 blur-[65px] pointer-events-none"></div>

          {/* Card Header */}
          <div className="flex items-center gap-3 border-b border-zinc-900/60 pb-4 mb-4">
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400">
              <TrendingUp className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Execution Analysis
            </h3>
          </div>

          {/* Execution details columns */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 py-2">
            <div className="space-y-3">
              <div>
                <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  Tech Complexity
                </span>
                <div className="text-xl font-bold text-coral-400 text-orange-400 mt-1">
                  {idea.industry === "DeFi / Web3" ? "High" : "Moderate"}
                </div>
              </div>
              <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
                {idea.industry === "DeFi / Web3"
                  ? "Requires specialized blockchain engineers (Solidity/Rust) and advanced cryptography knowledge."
                  : "Leverages standard cloud deployment APIs and standard SaaS pipelines."}
              </p>
              {/* Complexity Progress bar */}
              <div className="w-full h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-orange-500 to-red-500 rounded-full"
                  style={{ width: idea.industry === "DeFi / Web3" ? "85%" : "55%" }}
                ></div>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  Time To MVP
                </span>
                <div className="text-xl font-bold text-indigo-400 mt-1">
                  {idea.timeline}
                </div>
              </div>
              <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
                Estimated timeline for core system deployment with basic security audits and foundational tests completed.
              </p>
              {/* Timeline Progress bar */}
              <div className="w-full h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: "45%" }}></div>
              </div>
            </div>
          </div>
        </div>

        {/* Revenue Model Card */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] relative overflow-hidden flex flex-col justify-between min-h-[220px]">
          <div className="absolute top-0 right-0 w-[150px] h-[150px] bg-purple-500/5 blur-[50px] pointer-events-none"></div>

          {/* Card Header */}
          <div className="flex items-center justify-between border-b border-zinc-900/60 pb-4 mb-4">
            <div className="flex items-center gap-3">
              <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400">
                <DollarSign className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Revenue Model
              </h3>
            </div>
            <button className="text-zinc-500 hover:text-zinc-300">
              <MoreHorizontal className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  Primary Source
                </span>
                <div className="text-xs font-semibold text-zinc-100 mt-0.5">
                  {idea.industry === "DeFi / Web3" ? "Transaction Fees" : "Monthly Subscriptions"}
                </div>
              </div>
              <div className="text-xs font-bold text-zinc-300 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded">
                {idea.industry === "DeFi / Web3" ? "0.3%" : "$49/mo"}
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  Secondary Source
                </span>
                <div className="flex items-center gap-1.5 mt-1">
                  <span className="inline-block text-[9px] font-bold text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                    B2B API
                  </span>
                  <span className="inline-block text-[9px] font-bold text-purple-400 bg-purple-500/10 border border-purple-500/20 px-2 py-0.5 rounded">
                    SaaS Tier
                  </span>
                </div>
              </div>
            </div>

            {/* Estimated Year 1 ARR */}
            <div className="border-t border-zinc-900/60 pt-3">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                Est. Year 1 ARR (Optimistic)
              </span>
              <div className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-purple-400 via-pink-400 to-rose-400 drop-shadow-[0_2px_10px_rgba(219,39,119,0.2)] mt-0.5">
                $1.2M - $2.5M
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Graph and Investor Fit */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Growth vs Cost Chart */}
        <div className="lg:col-span-2 bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[300px]">
          <div className="flex items-center justify-between mb-4 border-b border-zinc-900/60 pb-3">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Growth vs Cost
            </h3>
            {/* Chart Legend */}
            <div className="flex items-center gap-4 text-[10px] font-semibold">
              <div className="flex items-center gap-1.5 text-zinc-400">
                <span className="w-2 h-2 rounded-full bg-indigo-500"></span>
                Revenue
              </div>
              <div className="flex items-center gap-1.5 text-zinc-400">
                <span className="w-2 h-2 rounded-full bg-pink-500 border border-dashed border-pink-400"></span>
                Infra Cost
              </div>
            </div>
          </div>

          {/* SVG Vector Line Chart representation */}
          <div className="flex-1 w-full min-h-[180px] relative flex items-end">
            <svg className="w-full h-[180px] overflow-visible" xmlns="http://www.w3.org/2000/svg">
              {/* Grid Lines */}
              <line x1="0" y1="30" x2="100%" y2="30" stroke="rgba(255,255,255,0.02)" strokeWidth="1" />
              <line x1="0" y1="80" x2="100%" y2="80" stroke="rgba(255,255,255,0.02)" strokeWidth="1" />
              <line x1="0" y1="130" x2="100%" y2="130" stroke="rgba(255,255,255,0.02)" strokeWidth="1" />
              <line x1="0" y1="170" x2="100%" y2="170" stroke="rgba(255,255,255,0.04)" strokeWidth="1" />

              {/* Dynamic Revenue Exponential Curve */}
              <path
                d="M 10 160 Q 150 140, 280 80 T 500 15"
                fill="none"
                stroke="url(#blue-grad)"
                strokeWidth="3.5"
                strokeLinecap="round"
                className="drop-shadow-[0_4px_10px_rgba(99,102,241,0.35)]"
              />

              {/* Infrastructure Linear Cost path */}
              <path
                d="M 10 165 C 120 158, 250 152, 500 145"
                fill="none"
                stroke="#ec4899"
                strokeWidth="2"
                strokeDasharray="4,4"
                strokeLinecap="round"
              />

              {/* Gradients */}
              <defs>
                <linearGradient id="blue-grad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#4f46e5" />
                  <stop offset="100%" stopColor="#818cf8" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          {/* Time markers footer */}
          <div className="flex items-center justify-between text-[9px] font-bold text-zinc-600 uppercase tracking-widest mt-2 border-t border-zinc-900/60 pt-3">
            <span>Year 1</span>
            <span>Year 2</span>
            <span>Year 3</span>
            <span>Year 4</span>
            <span>Year 5</span>
          </div>
        </div>

        {/* Investor Fit Summary Card */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[300px]">
          <div>
            {/* Card Header */}
            <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3 mb-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Investor Fit Summary
              </h3>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[8px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-400 uppercase tracking-wider">
                Seed Stage Target
              </span>
            </div>

            {/* Checklist elements */}
            <div className="space-y-4">
              {/* Bullet 1 */}
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <h4 className="text-xs font-bold text-white">Strong Defensibility</h4>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                    {idea.industry === "DeFi / Web3"
                      ? "Proprietary liquidity matching algorithm provides a significant moat against generic DEX forks."
                      : "Multi-layered proprietary caching architecture and vector pipeline provides competitive defenses."}
                  </p>
                </div>
              </div>

              {/* Bullet 2 */}
              <div className="flex items-start gap-3">
                <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <h4 className="text-xs font-bold text-white">Clear Market Need</h4>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                    Solves current fragmentation issues across production environments and provides high developer velocity.
                  </p>
                </div>
              </div>

              {/* Bullet 3 */}
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-4 h-4 text-orange-500 shrink-0 mt-0.5" />
                <div className="space-y-0.5">
                  <h4 className="text-xs font-bold text-white">Regulatory Risk</h4>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                    High exposure to evolving AI / Web3 regulations in US/EU markets requiring robust legal strategy.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section Recommended Tech Stack */}
      <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
        <h3 className="text-xs font-bold text-zinc-400 uppercase tracking-widest mb-4">
          Recommended Tech Stack
        </h3>
        <div className="flex flex-wrap items-center gap-3">
          {techStack.map((tech) => (
            <div
              key={tech.name}
              className={`flex items-center gap-2 px-3.5 py-1.5 text-xs font-bold rounded-lg border ${tech.bg}`}
            >
              <span className="w-4 h-4 rounded-md bg-white/10 flex items-center justify-center text-[9px] font-extrabold text-white shrink-0">
                {tech.label}
              </span>
              {tech.name}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
