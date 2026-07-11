"use client";

import React, { useState } from "react";
import {
  TrendingUp,
  Search,
  FileDown,
  Share2,
  PieChart,
  LineChart,
  ShieldCheck,
  AlertOctagon,
  CheckCircle2,
} from "lucide-react";
import { toast } from "sonner";

export default function InvestorPage() {
  const [modelTier, setModelTier] = useState<"conservative" | "base" | "aggressive">("base");

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Search row breadcrumbs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            Financial & Pitching Suite
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Investor Analysis
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search analytics..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* Heading Details */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <p className="text-xs text-zinc-500 max-w-xl leading-relaxed">
          Comprehensive validation metrics and funding readiness for Project Alpha.
        </p>

        {/* Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toast.success("Pitch-deck metric PDF exported!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
          >
            <FileDown className="w-3.5 h-3.5" />
            Export PDF
          </button>
          <button
            onClick={() => toast.success("Secure sharing link generated!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.3)] rounded-xl transition-all"
          >
            <Share2 className="w-3.5 h-3.5" />
            Share Report
          </button>
        </div>
      </div>

      {/* Row 1 Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Confidence Score */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[220px] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-[120px] h-[120px] bg-indigo-500/5 blur-[45px] pointer-events-none"></div>

          <div className="border-b border-zinc-900/60 pb-3">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
              Confidence Score
            </span>
          </div>

          <div className="space-y-2 my-2">
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-black text-white tracking-tight">87</span>
              <span className="text-xs font-bold text-emerald-400">+4.2 pts</span>
            </div>
            <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
              Top decile performance compared to similar stage SaaS startups. Strong signals in market timing.
            </p>
          </div>

          <div className="text-[9px] font-bold text-zinc-600 uppercase tracking-widest pt-2 border-t border-zinc-900/60">
            Based on 14 validation vectors
          </div>
        </div>

        {/* Funding Readiness */}
        <div className="lg:col-span-2 bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[220px] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-purple-500/5 blur-[70px] pointer-events-none"></div>

          <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3 mb-2">
            <div>
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Funding Readiness
              </span>
              <span className="text-xs font-bold text-zinc-200 block mt-0.5">
                Target: Series A ($12M - $15M)
              </span>
            </div>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[8px] font-bold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 uppercase tracking-wider">
              82% Prepared
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-2">
            {/* Meter 1 */}
            <div className="space-y-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Team & Execution
              </span>
              <span className="text-base font-extrabold text-white">95%</span>
              <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: "95%" }}></div>
              </div>
            </div>

            {/* Meter 2 */}
            <div className="space-y-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Financial Model
              </span>
              <span className="text-base font-extrabold text-white">70%</span>
              <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: "70%" }}></div>
              </div>
            </div>

            {/* Meter 3 */}
            <div className="space-y-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Go-To-Market
              </span>
              <span className="text-base font-extrabold text-white">80%</span>
              <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 rounded-full" style={{ width: "80%" }}></div>
              </div>
            </div>
          </div>

          {/* Alert notice */}
          <div className="border-t border-zinc-900/60 pt-3 flex items-start gap-2.5 text-[10px] text-zinc-550 leading-relaxed font-semibold">
            <AlertOctagon className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
            <p>
              Focus needed on hardening the financial model. Recommend stress-testing churn assumptions before investor outreach.
            </p>
          </div>
        </div>
      </div>

      {/* Row 2: TAM/SAM/SOM and Revenue Projection */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* TAM/SAM/SOM Doughnut Chart */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[300px]">
          <div className="border-b border-zinc-900/60 pb-3 mb-2 flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <PieChart className="w-4 h-4 text-indigo-400" />
              Market Sizing
            </h3>
            <span className="text-[8.5px] font-semibold text-zinc-650">TAM / SAM / SOM</span>
          </div>

          {/* Doughnut SVG */}
          <div className="flex-1 flex items-center justify-center py-2 relative">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle cx="64" cy="64" r="48" className="stroke-indigo-500/20" strokeWidth="8" fill="transparent" />
              <circle cx="64" cy="64" r="48" className="stroke-indigo-500" strokeWidth="8" fill="transparent" strokeDasharray={301} strokeDashoffset={75} strokeLinecap="round" />
              <circle cx="64" cy="64" r="48" className="stroke-purple-500" strokeWidth="8" fill="transparent" strokeDasharray={301} strokeDashoffset={200} strokeLinecap="round" />
            </svg>
            <div className="absolute text-center">
              <span className="text-sm font-black text-white">$12B</span>
              <span className="text-[8px] font-bold text-zinc-600 block uppercase tracking-widest mt-0.5">TAM</span>
            </div>
          </div>

          <div className="space-y-1.5 text-[9.5px] font-semibold text-zinc-500 border-t border-zinc-900/60 pt-3">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                TAM (Global)
              </div>
              <span className="text-zinc-300 font-extrabold">$12.4B</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-purple-500"></span>
                SAM (US/EU)
              </div>
              <span className="text-zinc-300 font-extrabold">$1.1B</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-zinc-700"></span>
                SOM (Obtainable)
              </div>
              <span className="text-zinc-300 font-extrabold">$850M</span>
            </div>
          </div>
        </div>

        {/* Revenue Projection 5 YR */}
        <div className="lg:col-span-2 bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[300px]">
          <div className="border-b border-zinc-900/60 pb-3 mb-3 flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <LineChart className="w-4 h-4 text-purple-400" />
              Revenue Projection (5 YR)
            </h3>

            {/* Toggle filters */}
            <div className="flex items-center bg-[#070709] border border-zinc-900 p-0.5 rounded-lg text-[8.5px] font-extrabold tracking-widest uppercase">
              <button
                onClick={() => setModelTier("conservative")}
                className={`px-2.5 py-1.5 rounded-md transition-all ${
                  modelTier === "conservative" ? "bg-zinc-900 text-white" : "text-zinc-600 hover:text-zinc-400"
                }`}
              >
                Conservative
              </button>
              <button
                onClick={() => setModelTier("base")}
                className={`px-2.5 py-1.5 rounded-md transition-all ${
                  modelTier === "base" ? "bg-zinc-900 text-white" : "text-zinc-600 hover:text-zinc-400"
                }`}
              >
                Base
              </button>
              <button
                onClick={() => setModelTier("aggressive")}
                className={`px-2.5 py-1.5 rounded-md transition-all ${
                  modelTier === "aggressive" ? "bg-zinc-900 text-white" : "text-zinc-600 hover:text-zinc-400"
                }`}
              >
                Aggressive
              </button>
            </div>
          </div>

          {/* Area Graph Projection */}
          <div className="flex-1 w-full min-h-[160px] relative flex items-end">
            <svg className="w-full h-[160px] overflow-visible" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="area-grad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.18" />
                  <stop offset="100%" stopColor="#4f46e5" stopOpacity="0.01" />
                </linearGradient>
              </defs>

              {/* Area filled polygon */}
              <path
                d="M 10 150 C 100 130, 220 90, 500 10 L 500 150 Z"
                fill="url(#area-grad)"
              />

              {/* Solid upper border curve */}
              <path
                d="M 10 150 C 100 130, 220 90, 500 10"
                fill="none"
                stroke="#4f46e5"
                strokeWidth="3.5"
                strokeLinecap="round"
                className="drop-shadow-[0_4px_10px_rgba(99,102,241,0.25)]"
              />
            </svg>
          </div>

          <div className="flex items-center justify-between text-[9px] font-bold text-zinc-600 uppercase tracking-widest mt-2 border-t border-zinc-900/60 pt-3">
            <span>Y1</span>
            <span>Y2</span>
            <span>Y3</span>
            <span>Y4</span>
            <span>Y5</span>
          </div>
        </div>
      </div>

      {/* Row 3: Risk Assessment and Market Fit Signals */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Assessment */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <div className="border-b border-zinc-900/60 pb-3 mb-4 flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Risk Assessment
            </h3>
            {/* Legend */}
            <div className="flex items-center gap-2 text-[8px] font-extrabold uppercase text-zinc-600">
              <span>Low</span>
              <span>•</span>
              <span>Medium</span>
              <span>•</span>
              <span>High</span>
            </div>
          </div>

          <div className="space-y-4">
            {/* Grid 1 */}
            <div className="space-y-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Market Risk
              </span>
              <div className="flex gap-1.5">
                <div className="h-2 flex-1 bg-purple-500 rounded"></div>
                <div className="h-2 flex-1 bg-purple-500 rounded"></div>
                <div className="h-2 flex-1 bg-purple-500 rounded"></div>
                <div className="h-2 flex-1 bg-[#0c0c0e] border border-zinc-900 rounded"></div>
              </div>
            </div>

            {/* Grid 2 */}
            <div className="space-y-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Technical Risk
              </span>
              <div className="flex gap-1.5">
                <div className="h-2 flex-1 bg-indigo-500 rounded"></div>
                <div className="h-2 flex-1 bg-indigo-500 rounded"></div>
                <div className="h-2 flex-1 bg-[#0c0c0e] border border-zinc-900 rounded"></div>
                <div className="h-2 flex-1 bg-[#0c0c0e] border border-zinc-900 rounded"></div>
              </div>
            </div>

            {/* Grid 3 */}
            <div className="space-y-1.5">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Execution Risk
              </span>
              <div className="flex gap-1.5">
                <div className="h-2 flex-1 bg-indigo-500 rounded"></div>
                <div className="h-2 flex-1 bg-indigo-500 rounded"></div>
                <div className="h-2 flex-1 bg-indigo-500 rounded"></div>
                <div className="h-2 flex-1 bg-[#0c0c0e] border border-zinc-900 rounded"></div>
              </div>
            </div>
          </div>
        </div>

        {/* Market Fit Signals */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <div className="border-b border-zinc-900/60 pb-3 mb-4">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Market Fit Signals
            </h3>
          </div>

          <div className="space-y-4">
            {/* bullet 1 */}
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-4.5 h-4.5 text-indigo-400 shrink-0 mt-0.5" />
              <div className="space-y-0.5">
                <h4 className="text-[11px] font-bold text-white">Strong Pain Point Validation</h4>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  85% of surveyed beta users reported saving &gt;10 hours weekly.
                </p>
              </div>
            </div>

            {/* bullet 2 */}
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-4.5 h-4.5 text-indigo-400 shrink-0 mt-0.5" />
              <div className="space-y-0.5">
                <h4 className="text-[11px] font-bold text-white">High Willingness to Pay</h4>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  Pricing sensitivity analysis indicates acceptable ACV of $10k+.
                </p>
              </div>
            </div>

            {/* bullet 3 */}
            <div className="flex items-start gap-3">
              <CheckCircle2 className="w-4.5 h-4.5 text-indigo-400 shrink-0 mt-0.5" />
              <div className="space-y-0.5">
                <h4 className="text-[11px] font-bold text-white">Scalable Acquisition Channel</h4>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  Currently testing organic vs paid efficiency. CAC needs optimization.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
