"use client";

import React from "react";
import {
  Target,
  Search,
  FileDown,
  Share2,
  TrendingUp,
  Scale,
  Sparkles,
  ArrowRight,
  Plus,
} from "lucide-react";
import { toast } from "sonner";

export default function StrategyLabPage() {
  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Breadcrumb header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            Workspace / Strategic Design
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            AI Strategy Lab
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search analysis, roadmaps..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-650"
          />
        </div>
      </div>

      {/* Main Title and strategy tags */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[8px] font-bold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 uppercase tracking-wider">
              Strategy Lab
            </span>
            <span className="text-[10px] font-semibold text-zinc-500">
              78% product-market fit potential
            </span>
          </div>
          <h2 className="text-2xl font-extrabold text-white">
            Omni-Channel AI Platform
          </h2>
          <p className="text-xs text-zinc-550 max-w-xl leading-relaxed">
            Focus optimization on enterprise integration channels and B2B developers ecosystems.
          </p>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toast.success("GTM strategy sheet PDF exported!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
          >
            <FileDown className="w-3.5 h-3.5" />
            Export PDF
          </button>
          <button
            onClick={() => toast.success("Strategy board shared successfully!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.3)] rounded-xl transition-all"
          >
            <Share2 className="w-3.5 h-3.5" />
            Share Board
          </button>
        </div>
      </div>

      {/* Grid Content splits */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (Wide): Market Positioning Graph & Monetization */}
        <div className="lg:col-span-2 space-y-6">
          {/* Market Positioning Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[300px]">
            <div className="border-b border-zinc-900/60 pb-3 mb-4">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Market Positioning
              </h3>
              <p className="text-[10px] text-zinc-500 font-semibold mt-1">
                AI calculated vector mapping against top 10 competitors.
              </p>
            </div>

            {/* SVG Scatter Plot grid */}
            <div className="flex-1 w-full min-h-[160px] relative flex items-center justify-center">
              <svg className="w-full h-[160px] overflow-visible" xmlns="http://www.w3.org/2000/svg">
                {/* Axes grid lines */}
                <line x1="50%" y1="0" x2="50%" y2="100%" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
                <line x1="0" y1="50%" x2="100%" y2="50%" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />

                {/* Legend / Axis Labels */}
                <text x="5" y="15" fill="rgba(255,255,255,0.2)" fontSize="8" fontWeight="bold">HIGH PRICING</text>
                <text x="5" y="155" fill="rgba(255,255,255,0.2)" fontSize="8" fontWeight="bold">LOW PRICING</text>
                <text x="85%" y="95" fill="rgba(255,255,255,0.2)" fontSize="8" fontWeight="bold">MODERN STACK</text>
                <text x="5" y="95" fill="rgba(255,255,255,0.2)" fontSize="8" fontWeight="bold">LEGACY SYSTEMS</text>

                {/* Coordinate Competitor Dots */}
                <circle cx="20%" cy="30%" r="5" fill="#4b5563" />
                <text x="16%" y="22%" fill="#9ca3af" fontSize="8" fontWeight="bold">Legacy A</text>

                <circle cx="80%" cy="70%" r="5" fill="#4b5563" />
                <text x="76%" y="62%" fill="#9ca3af" fontSize="8" fontWeight="bold">Startup B</text>

                <circle cx="35%" cy="80%" r="5" fill="#4b5563" />
                <text x="31%" y="72%" fill="#9ca3af" fontSize="8" fontWeight="bold">BigCorp C</text>

                {/* Target Node: IdeaGPT (You) */}
                <circle cx="65%" cy="40%" r="7" fill="#4f46e5" className="drop-shadow-[0_0_8px_rgba(79,70,229,0.8)]" />
                <text x="61%" y="30%" fill="#a5b4fc" fontSize="9" fontWeight="bold">IdeaGPT (You)</text>
              </svg>
            </div>
          </div>

          {/* Monetization Models Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
              <Scale className="w-4 h-4 text-purple-400" />
              Monetization Models
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Model 1 */}
              <div className="bg-[#070709] border border-zinc-900/60 rounded-xl p-4 space-y-4 hover:border-zinc-800 transition-all flex flex-col justify-between">
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-white">Usage-Based Tiered</h4>
                    <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold bg-green-500/10 border border-green-500/20 text-green-400 uppercase tracking-wide">
                      Recommended
                    </span>
                  </div>
                  <p className="text-[10px] text-zinc-550 leading-relaxed font-semibold">
                    Core developers pricing structures for modular API platform usage.
                  </p>
                </div>
                <div className="border-t border-zinc-900 pt-3 flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  <div>
                    <span>Base Fee</span>
                    <span className="text-white block mt-0.5">$49/mo</span>
                  </div>
                  <div className="text-right">
                    <span>LTV Conv</span>
                    <span className="text-indigo-400 block mt-0.5">High (64%)</span>
                  </div>
                </div>
              </div>

              {/* Model 2 */}
              <div className="bg-[#070709] border border-zinc-900/60 rounded-xl p-4 space-y-4 hover:border-zinc-800 transition-all flex flex-col justify-between">
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-white">Flat Enterprise Seat</h4>
                    <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-500 uppercase tracking-wide">
                      Alternative
                    </span>
                  </div>
                  <p className="text-[10px] text-zinc-550 leading-relaxed font-semibold">
                    Dedicated flat scaling license agreements per seat metrics.
                  </p>
                </div>
                <div className="border-t border-zinc-900 pt-3 flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                  <div>
                    <span>Per Seat</span>
                    <span className="text-white block mt-0.5">$199/mo</span>
                  </div>
                  <div className="text-right">
                    <span>LTV Conv</span>
                    <span className="text-zinc-400 block mt-0.5">Med (41%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Growth Vectors & Core Features Scopes */}
        <div className="space-y-6">
          {/* Growth Vectors */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[250px]">
            <div>
              <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4">
                Growth Vectors
              </h3>

              <div className="space-y-4">
                {/* Item 1 */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">Developer API Ecosystem</span>
                    <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 uppercase tracking-wide">
                      High ROI
                    </span>
                  </div>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-semibold">
                    Target dev-rel integrations and sandbox environments.
                  </p>
                </div>

                {/* Item 2 */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white">B2B Content Syndication</span>
                    <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-500 uppercase tracking-wide">
                      Mid-Term
                    </span>
                  </div>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-semibold">
                    Publishing technical whitepapers for enterprise leads.
                  </p>
                </div>
              </div>
            </div>

            <button
              onClick={() => toast.success("Additional growth acquisition channels simulated!")}
              className="w-full mt-4 py-2.5 text-[9px] font-bold text-white bg-[#0c0c0e] border border-zinc-850 hover:bg-zinc-800 hover:border-zinc-700 active:scale-[0.98] rounded-xl transition-all uppercase tracking-widest flex items-center justify-center gap-2"
            >
              <Plus className="w-3.5 h-3.5 text-zinc-500" />
              Generate More
            </button>
          </div>

          {/* Core Features AI-Scoring */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              Core Features AI-Scoring
            </h3>

            <div className="space-y-4">
              {/* Bar 1 */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                  <span>Predictive Analytics Dashboard</span>
                  <span className="text-white font-extrabold">94% Impact</span>
                </div>
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: "94%" }}></div>
                </div>
              </div>

              {/* Bar 2 */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                  <span>Automated Reporting Engine</span>
                  <span className="text-white font-extrabold">75% Impact</span>
                </div>
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-500 rounded-full" style={{ width: "75%" }}></div>
                </div>
              </div>

              {/* Bar 3 */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
                  <span>Real-time Collaboration</span>
                  <span className="text-white font-extrabold">45% Impact</span>
                </div>
                <div className="w-full h-1.5 bg-zinc-950 rounded-full overflow-hidden">
                  <div className="h-full bg-zinc-700 rounded-full" style={{ width: "45%" }}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
