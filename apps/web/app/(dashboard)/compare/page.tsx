"use client";

import React from "react";
import {
  GitCompare,
  Search,
  Share2,
  Bookmark,
  TrendingUp,
  Scale,
  Sparkles,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import { toast } from "sonner";

export default function ComparePage() {
  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Breadcrumb header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            Research & Analytics
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Compare Ideas
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search concepts..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* Title Segment and buttons */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <p className="text-xs text-zinc-500 max-w-xl leading-relaxed">
          Strategic analysis: Project Nebula vs. Project Orion
        </p>

        {/* Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toast.success("Comparative review exported!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
          >
            <Share2 className="w-3.5 h-3.5" />
            Export
          </button>
          <button
            onClick={() => toast.success("Comparative analysis saved!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            <Bookmark className="w-3.5 h-3.5" />
            Save
          </button>
        </div>
      </div>

      {/* Row 1 Concept Cards & Radar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Concept Alpha: Project Nebula */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[260px] relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-[120px] h-[120px] bg-indigo-500/5 blur-[45px] pointer-events-none"></div>

          <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3">
            <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
              Concept Alpha
            </span>
            <span className="w-4 h-4 rounded-full bg-indigo-500/10 flex items-center justify-center text-[10px] text-indigo-400 font-extrabold">
              α
            </span>
          </div>

          <div className="space-y-4 my-3 text-center sm:text-left flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <h3 className="text-base font-extrabold text-white">Project Nebula</h3>
              <p className="text-[10px] text-zinc-500 font-medium">B2B SaaS Data Pipelines</p>
            </div>

            {/* Score Ring */}
            <div className="relative flex items-center justify-center w-16 h-16 shrink-0 mx-auto sm:mx-0">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle cx="32" cy="32" r="28" className="stroke-zinc-800" strokeWidth="3" fill="transparent" />
                <circle cx="32" cy="32" r="28" className="stroke-indigo-500" strokeWidth="3" fill="transparent" strokeDasharray={175} strokeDashoffset={175 - (175 * 80) / 100} />
              </svg>
              <div className="absolute text-center">
                <span className="text-base font-black text-white">80</span>
              </div>
            </div>
          </div>

          <div className="border-t border-zinc-900/60 pt-3 flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
            <div>
              <span>Est. ARR (Y1)</span>
              <span className="text-white block mt-0.5">$45k</span>
            </div>
            <div className="text-right">
              <span>Churn Risk</span>
              <span className="text-red-400 block mt-0.5">High</span>
            </div>
          </div>
        </div>

        {/* Central Card: SVG Radar Chart */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[260px]">
          <div className="border-b border-zinc-900/60 pb-3 mb-2 flex items-center justify-between">
            <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
              Performance Graph
            </span>
            {/* Legend */}
            <div className="flex items-center gap-3 text-[8.5px] font-bold">
              <div className="flex items-center gap-1 text-zinc-400">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                Nebula
              </div>
              <div className="flex items-center gap-1 text-zinc-400">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                Orion
              </div>
            </div>
          </div>

          {/* SVG Spider Radar chart */}
          <div className="flex-1 flex items-center justify-center py-2">
            <svg className="w-40 h-40 overflow-visible" viewBox="0 0 100 100">
              {/* Web Polygons */}
              <polygon points="50,10 90,40 75,85 25,85 10,40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <polygon points="50,25 80,45 68,76 32,76 20,45" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <polygon points="50,40 70,50 62,68 38,68 30,50" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />

              {/* Axis Web lines */}
              <line x1="50" y1="50" x2="50" y2="10" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="50" y1="50" x2="90" y2="40" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="50" y1="50" x2="75" y2="85" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="50" y1="50" x2="25" y2="85" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
              <line x1="50" y1="50" x2="10" y2="40" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />

              {/* Project Nebula Area path (Indigo) */}
              <polygon points="50,15 82,42 66,74 38,80 24,44" fill="rgba(99, 102, 241, 0.15)" stroke="#4f46e5" strokeWidth="1.5" />

              {/* Project Orion Area path (Purple) */}
              <polygon points="50,30 76,46 72,70 30,72 16,42" fill="rgba(168, 85, 247, 0.15)" stroke="#a855f7" strokeWidth="1.5" />
            </svg>
          </div>

          <div className="text-center text-[9px] font-bold text-zinc-650 uppercase tracking-widest mt-1">
            5 Dimension Vector Plot
          </div>
        </div>

        {/* Concept Beta: Project Orion */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[260px] relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-[120px] h-[120px] bg-purple-500/5 blur-[45px] pointer-events-none"></div>

          <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3">
            <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
              Concept Beta
            </span>
            <span className="w-4 h-4 rounded-full bg-purple-500/10 flex items-center justify-center text-[10px] text-purple-400 font-extrabold">
              β
            </span>
          </div>

          <div className="space-y-4 my-3 text-center sm:text-left flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div className="space-y-1">
              <h3 className="text-base font-extrabold text-white">Project Orion</h3>
              <p className="text-[10px] text-zinc-500 font-medium">D2C Fintech App</p>
            </div>

            {/* Score Ring */}
            <div className="relative flex items-center justify-center w-16 h-16 shrink-0 mx-auto sm:mx-0">
              <svg className="w-16 h-16 transform -rotate-90">
                <circle cx="32" cy="32" r="28" className="stroke-zinc-800" strokeWidth="3" fill="transparent" />
                <circle cx="32" cy="32" r="28" className="stroke-purple-500" strokeWidth="3" fill="transparent" strokeDasharray={175} strokeDashoffset={175 - (175 * 65) / 100} />
              </svg>
              <div className="absolute text-center">
                <span className="text-base font-black text-white">65</span>
              </div>
            </div>
          </div>

          <div className="border-t border-zinc-900/60 pt-3 flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
            <div>
              <span>Est. ARR (Y1)</span>
              <span className="text-white block mt-0.5">$120k</span>
            </div>
            <div className="text-right">
              <span>Churn Risk</span>
              <span className="text-emerald-400 block mt-0.5">Low</span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: In-Depth Dimension Analysis */}
      <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
        <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-5">
          In-Depth Dimension Analysis
        </h3>

        <div className="space-y-6">
          {/* Dimension 1 */}
          <div className="space-y-2">
            <div className="flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
              <span>Technical Complexity</span>
              <span className="text-zinc-400">Nebula (High) vs Orion (Mod)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: "85%" }}></div>
                </div>
              </div>
              <div className="space-y-1">
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full" style={{ width: "45%" }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Dimension 2 */}
          <div className="space-y-2">
            <div className="flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
              <span>Market Opportunity (TAM)</span>
              <span className="text-zinc-400">Nebula (Mod) vs Orion (High)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: "50%" }}></div>
                </div>
              </div>
              <div className="space-y-1">
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full" style={{ width: "90%" }}></div>
                </div>
              </div>
            </div>
          </div>

          {/* Dimension 3 */}
          <div className="space-y-2">
            <div className="flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
              <span>Recruiter Score (Talent Access)</span>
              <span className="text-zinc-400">Nebula (Hard) vs Orion (Abundant)</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: "40%" }}></div>
                </div>
              </div>
              <div className="space-y-1">
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full" style={{ width: "80%" }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: AI Strategic Recommendation */}
      <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] relative overflow-hidden group">
        <div className="absolute top-0 right-0 w-[150px] h-[150px] bg-indigo-500/5 blur-[50px] pointer-events-none"></div>

        <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          AI Strategic Recommendation
        </h3>

        <div className="space-y-4 text-xs text-zinc-500 leading-relaxed font-medium">
          <p>
            While <span className="text-zinc-300 font-semibold">Project Nebula</span> presents a higher barrier to entry and technical risk, its B2B positioning offers stronger long-term moats. <span className="text-purple-400 font-semibold">Project Orion</span> has immediate consumer appeal and a larger TAM, but faces intense competition and talent acquisition costs.
          </p>
          <div className="border-t border-zinc-900/60 pt-3 flex items-start gap-2.5">
            <Scale className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <p>
              <span className="text-white font-bold">Verdict:</span> Pursue Project Nebula if initial capital &gt; $2M and technical co-founder is secured. Otherwise, Project Orion provides a faster path to initial revenue validation.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
