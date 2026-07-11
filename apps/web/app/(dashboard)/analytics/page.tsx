"use client";

import React, { useState } from "react";
import {
  Activity,
  Search,
  FileDown,
  TrendingUp,
  Clock,
  CheckCircle,
  AlertOctagon,
  Calendar,
  Globe,
  MoreVertical,
  ChevronRight,
} from "lucide-react";
import { toast } from "sonner";

export default function AnalyticsPage() {
  const [timeFilter, setTimeFilter] = useState("Last 24 Hours");

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Breadcrumb header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            System Infrastructure
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Platform Operations
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search operations..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* Main Title segment */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <p className="text-xs text-zinc-500 max-w-xl leading-relaxed">
          Real-time monitoring and generative metrics for IdeaGPT cluster.
        </p>

        {/* Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          <select
            value={timeFilter}
            onChange={(e) => {
              setTimeFilter(e.target.value);
              toast.success(`Metrics filtered by ${e.target.value}`);
            }}
            className="bg-[#0c0c0e] border border-zinc-800 text-xs text-zinc-300 px-3 py-2 rounded-xl outline-none font-semibold cursor-pointer"
          >
            <option>Last 1 Hour</option>
            <option>Last 24 Hours</option>
            <option>Last 7 Days</option>
            <option>Last 30 Days</option>
          </select>

          <button
            onClick={() => toast.success("Ops metrics report exported!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            <FileDown className="w-3.5 h-3.5" />
            Export Report
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* KPI 1 */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[140px] relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              AI Request Volume
            </span>
            <span className="w-6 h-6 rounded-md bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <Activity className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-white tracking-tight">1.24M</div>
            <div className="flex items-center gap-1 text-[9px] font-bold text-emerald-400 mt-1">
              <TrendingUp className="w-3 h-3" />
              +14.2% vs yesterday
            </div>
          </div>
        </div>

        {/* KPI 2 */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[140px] relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              Tokens Processed
            </span>
            <span className="w-6 h-6 rounded-md bg-purple-500/10 flex items-center justify-center text-purple-400">
              <TrendingUp className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-white tracking-tight">8.4B</div>
            <div className="flex items-center gap-1 text-[9px] font-bold text-emerald-400 mt-1">
              <TrendingUp className="w-3 h-3" />
              +8.1% vs yesterday
            </div>
          </div>
        </div>

        {/* KPI 3 */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[140px] relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              Avg Latency (Gen)
            </span>
            <span className="w-6 h-6 rounded-md bg-[#070709] border border-zinc-800 flex items-center justify-center text-zinc-500">
              <Clock className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-white tracking-tight">342<span className="text-sm font-bold text-zinc-500">ms</span></div>
            <div className="flex items-center gap-1 text-[9px] font-bold text-emerald-400 mt-1">
              <CheckCircle className="w-3 h-3" />
              -12ms p95 optimization
            </div>
          </div>
        </div>

        {/* KPI 4 */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[140px] relative overflow-hidden">
          <div className="flex justify-between items-start">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              Success Rate
            </span>
            <span className="w-6 h-6 rounded-md bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <CheckCircle className="w-3.5 h-3.5" />
            </span>
          </div>
          <div className="my-2">
            <div className="text-3xl font-black text-white tracking-tight">99.8%</div>
            <div className="flex items-center gap-1 text-[9px] font-bold text-red-400 mt-1">
              <AlertOctagon className="w-3 h-3" />
              0.2% timeout errors
            </div>
          </div>
        </div>
      </div>

      {/* Row 2 charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Global Inference Traffic */}
        <div className="lg:col-span-2 bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[320px]">
          <div className="border-b border-zinc-900/60 pb-3 mb-4 flex items-center justify-between">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider">
              Global Inference Traffic
            </h3>

            {/* Toggle tabs */}
            <div className="flex bg-[#070709] border border-zinc-900 p-0.5 rounded-lg text-[8.5px] font-bold uppercase">
              <button className="px-2.5 py-1 bg-zinc-900 text-white rounded-md">Req/s</button>
              <button className="px-2.5 py-1 text-zinc-600">Tokens/s</button>
            </div>
          </div>

          {/* Area spline chart */}
          <div className="flex-1 w-full min-h-[180px] relative flex items-end">
            <svg className="w-full h-[180px] overflow-visible" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="area-indigo" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#4f46e5" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="#4f46e5" stopOpacity="0.01" />
                </linearGradient>
              </defs>

              {/* Area */}
              <path
                d="M 5 170 C 80 130, 160 140, 240 80 C 320 120, 400 110, 500 20 L 500 170 Z"
                fill="url(#area-indigo)"
              />

              {/* Line */}
              <path
                d="M 5 170 C 80 130, 160 140, 240 80 C 320 120, 400 110, 500 20"
                fill="none"
                stroke="#4f46e5"
                strokeWidth="3.5"
                strokeLinecap="round"
                className="drop-shadow-[0_4px_12px_rgba(99,102,241,0.35)]"
              />
            </svg>
          </div>

          <div className="flex items-center justify-between text-[9px] font-bold text-zinc-600 uppercase tracking-widest mt-2 border-t border-zinc-900/60 pt-3">
            <span>00:00</span>
            <span>04:00</span>
            <span>08:00</span>
            <span>12:00</span>
            <span>16:00</span>
            <span>20:00</span>
          </div>
        </div>

        {/* Right side: Model Distribution & Clusters */}
        <div className="space-y-6 flex flex-col">
          {/* Model Distribution */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex-1 flex flex-col justify-between">
            <div>
              <div className="border-b border-zinc-900/60 pb-3 mb-4 flex items-center justify-between">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Model Distribution
                </h3>
                <button className="text-zinc-650">
                  <MoreVertical className="w-4.5 h-4.5" />
                </button>
              </div>

              <div className="space-y-3.5">
                {/* Model 1 */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                    <span>IdeaGPT-4.0-Turbo</span>
                    <span className="text-white">65%</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                    <div className="h-full bg-indigo-500 rounded-full" style={{ width: "65%" }}></div>
                  </div>
                </div>

                {/* Model 2 */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                    <span>IdeaGPT-3.5-Fast</span>
                    <span className="text-white">22%</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                    <div className="h-full bg-purple-500 rounded-full" style={{ width: "22%" }}></div>
                  </div>
                </div>

                {/* Model 3 */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                    <span>Idea-Embedding-v2</span>
                    <span className="text-white">10%</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                    <div className="h-full bg-zinc-700 rounded-full" style={{ width: "10%" }}></div>
                  </div>
                </div>

                {/* Model 4 */}
                <div className="space-y-1">
                  <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                    <span>Other Models</span>
                    <span className="text-white">3%</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                    <div className="h-full bg-zinc-800 rounded-full" style={{ width: "3%" }}></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Active Geographic Clusters */}
            <div className="border-t border-zinc-900/60 pt-4 mt-4">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block mb-2">
                Active Geographic Clusters
              </span>
              <div className="flex items-center justify-between bg-zinc-950 border border-zinc-900 rounded-xl p-3 hover:border-zinc-800 transition-colors cursor-pointer group">
                <div className="flex items-center gap-2">
                  <Globe className="w-4 h-4 text-indigo-400 shrink-0" />
                  <div className="space-y-0.5">
                    <span className="text-[10px] font-bold text-white block">US West (Silicon Valley)</span>
                    <span className="text-[9px] text-zinc-500 font-semibold block uppercase tracking-wider">
                      us-west-1 • 45.2% traffic
                    </span>
                  </div>
                </div>
                <ChevronRight className="w-4 h-4 text-zinc-600 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
