"use client";

import React from "react";
import {
  Boxes,
  Search,
  Share2,
  Play,
  Cpu,
  Settings2,
  TrendingUp,
  Server,
  Activity,
} from "lucide-react";
import { toast } from "sonner";

export default function ArchitecturePage() {
  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Breadcrumb header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            Workspace / System Architecture
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Architecture Visualizer
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search nodes..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-650"
          />
        </div>
      </div>

      {/* Editor Main Header controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
          High-fidelity topological mapping and system design studio. Visualize microservices, data pipelines, and cloud infrastructure with generative precision.
        </p>

        {/* Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toast.success("Topological spec architecture exported!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
          >
            <Share2 className="w-3.5 h-3.5" />
            Export
          </button>
          <button
            onClick={() => toast.success("Load simulation started! Peak load verified up to 5k RPS.")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.3)] rounded-xl transition-all"
          >
            <Play className="w-3.5 h-3.5" />
            Simulate Load
          </button>
        </div>
      </div>

      {/* Main Canvas grid splits */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (Wide): Topological Node Canvas */}
        <div className="lg:col-span-2">
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[460px] relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-zinc-800/[0.01] blur-[80px] pointer-events-none"></div>

            {/* Canvas status row */}
            <div className="flex items-center justify-between border-b border-zinc-900 pb-3 mb-6 text-[9px] font-bold text-zinc-550 uppercase tracking-widest">
              <span>Topological Map</span>
              <span>Zoom: 100%</span>
            </div>

            {/* Visual Node Diagram */}
            <div className="flex-1 flex flex-col items-center justify-center py-6 relative">
              {/* SVG Link lines between HTML boxes */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none" xmlns="http://www.w3.org/2000/svg">
                {/* Lines */}
                <line x1="50%" y1="60" x2="50%" y2="120" stroke="rgba(99, 102, 241, 0.2)" strokeWidth="1.5" />
                <line x1="50%" y1="170" x2="20%" y2="240" stroke="rgba(99, 102, 241, 0.2)" strokeWidth="1.5" />
                <line x1="50%" y1="170" x2="50%" y2="240" stroke="rgba(99, 102, 241, 0.2)" strokeWidth="1.5" />
                <line x1="50%" y1="170" x2="80%" y2="240" stroke="rgba(99, 102, 241, 0.2)" strokeWidth="1.5" />
              </svg>

              {/* Node Layout Tree */}
              <div className="w-full flex flex-col items-center gap-10 relative z-10">
                {/* Root node */}
                <div className="bg-[#0c0c0e] border border-zinc-850 rounded-xl p-4 w-[160px] text-center space-y-1 relative shadow-lg">
                  <span className="text-[8px] font-extrabold text-zinc-550 uppercase tracking-wide">Client</span>
                  <h4 className="text-xs font-bold text-white">Web Client</h4>
                  <p className="text-[9px] text-zinc-550 font-medium">React / Next.js</p>
                </div>

                {/* Gateway node */}
                <div className="bg-[#0c0c0e] border border-zinc-850 rounded-xl p-4 w-[160px] text-center space-y-1 relative shadow-lg">
                  <span className="text-[8px] font-extrabold text-zinc-550 uppercase tracking-wide">Gateway</span>
                  <h4 className="text-xs font-bold text-white">API Gateway</h4>
                  <p className="text-[9px] text-zinc-550 font-medium">Node / Express</p>
                </div>

                {/* Third level leaf nodes */}
                <div className="w-full flex justify-between gap-4 max-w-lg">
                  {/* Leaf 1 */}
                  <div className="bg-[#0c0c0e] border border-zinc-850 rounded-xl p-3.5 w-[120px] text-center space-y-1 relative shadow-lg">
                    <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-green-500"></span>
                    <span className="text-[8px] font-extrabold text-zinc-550 uppercase tracking-wide">Service</span>
                    <h4 className="text-xs font-bold text-white">Auth Service</h4>
                    <p className="text-[9px] text-zinc-550 font-medium">Go / gRPC</p>
                  </div>

                  {/* Leaf 2 */}
                  <div className="bg-[#0c0c0e] border border-indigo-500 rounded-xl p-3.5 w-[130px] text-center space-y-1 relative shadow-lg shadow-indigo-500/5">
                    <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
                    <span className="text-[8px] font-extrabold text-indigo-400 uppercase tracking-wide block font-bold">AI Engine</span>
                    <h4 className="text-xs font-bold text-white">AI Engine</h4>
                    <p className="text-[9px] text-zinc-550 font-medium">Python / FastAPI</p>
                  </div>

                  {/* Leaf 3 */}
                  <div className="bg-[#0c0c0e] border border-zinc-850 rounded-xl p-3.5 w-[120px] text-center space-y-1 relative shadow-lg">
                    <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-green-500"></span>
                    <span className="text-[8px] font-extrabold text-zinc-550 uppercase tracking-wide">Pipeline</span>
                    <h4 className="text-xs font-bold text-white">Data Pipeline</h4>
                    <p className="text-[9px] text-zinc-550 font-medium">Rust / Kafka</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Node Details & Telemetry */}
        <div className="space-y-6">
          {/* AI Engine Node info */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
              <Cpu className="w-4.5 h-4.5 text-indigo-400" />
              AI Engine Node
            </h3>

            <div className="space-y-4 text-xs font-semibold text-zinc-400">
              <div className="flex justify-between py-1 border-b border-zinc-900/60">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Type</span>
                <span className="text-zinc-200">Microservice</span>
              </div>
              <div className="flex justify-between py-1 border-b border-zinc-900/60">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Runtime</span>
                <span className="text-emerald-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                  Python 3.11
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Dependencies</span>
                <span className="text-zinc-250 flex items-center gap-1">
                  <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-400">PostgreSQL</span>
                  <span className="inline-block px-1.5 py-0.5 rounded text-[9px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-400">Redis</span>
                </span>
              </div>

              <button
                onClick={() => toast.success("Editor node configuration opened!")}
                className="w-full mt-2 py-2.5 text-[9px] font-bold text-white bg-[#0c0c0e] border border-zinc-850 hover:bg-zinc-800 hover:border-zinc-700 active:scale-[0.98] rounded-xl transition-all uppercase tracking-widest flex items-center justify-center gap-2"
              >
                <Settings2 className="w-3.5 h-3.5 text-zinc-500" />
                Edit Configuration
              </button>
            </div>
          </div>

          {/* Live Telemetry Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
              <Activity className="w-4.5 h-4.5 text-purple-400" />
              Live Telemetry
            </h3>

            <div className="space-y-4">
              {/* CPU */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                  <span>CPU Usage</span>
                  <span className="text-white">42%</span>
                </div>
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: "42%" }}></div>
                </div>
              </div>

              {/* Memory */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                  <span>Memory (RAM)</span>
                  <span className="text-white">2.4 GB</span>
                </div>
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full" style={{ width: "60%" }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
