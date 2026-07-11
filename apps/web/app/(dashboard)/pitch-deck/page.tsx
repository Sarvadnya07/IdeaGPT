"use client";

import React, { useState } from "react";
import {
  Presentation,
  Share2,
  Play,
  Sparkles,
  Search,
  CheckCircle,
  FileCode,
  AlertTriangle,
  FolderOpen,
  ArrowRight,
  Database,
  Link2,
} from "lucide-react";
import { toast } from "sonner";

interface Slide {
  number: number;
  title: string;
  preview: string;
  active?: boolean;
  status?: string;
}

export default function PitchDeckPage() {
  const [selectedSlide, setSelectedSlide] = useState(1);
  const [copilotInput, setCopilotInput] = useState("");

  const slides: Slide[] = [
    { number: 1, title: "The Problem", preview: "Legacy friction costs B2B $2T annually." },
    { number: 2, title: "Solution", preview: "Instant multi-network settlement engines." },
    { number: 3, title: "Market Size", preview: "$12.4B total addressable SaaS market size." },
    { number: 4, title: "Financial Projections", preview: "Generating...", status: "Generating..." },
  ];

  const handleRefine = (e: React.FormEvent) => {
    e.preventDefault();
    if (!copilotInput) return;
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 1500)),
      {
        loading: "Pitch Copilot is rendering infographic layouts...",
        success: "Slide refined! Bullet points converted to visual flow infographic.",
        error: "Failed to refine slide",
      }
    );
    setCopilotInput("");
  };

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Breadcrumb header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            Presentation Studios
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            AI Pitch Deck Generator
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search slides, assets..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* Editor Main Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-[8px] font-bold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 uppercase tracking-wider">
              Investor Ready
            </span>
            <span className="text-[10px] font-semibold text-zinc-500">
              Last saved: 2 mins ago
            </span>
          </div>
          <h2 className="text-2xl font-extrabold text-white">
            Series A - FinTech Disruptor
          </h2>
        </div>

        {/* Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toast.success("Pitch deck exported to PDF!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
          >
            <Share2 className="w-3.5 h-3.5" />
            Export
          </button>
          <button
            onClick={() => toast.success("Presenter mode loaded!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
          >
            <Play className="w-3.5 h-3.5" />
            Present
          </button>
          <button
            onClick={() => toast.success("Pitch deck refined globally!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            <Sparkles className="w-3.5 h-3.5" />
            AI Refine
          </button>
        </div>
      </div>

      {/* Editor Content Area splits */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Column 1: Slides list timeline */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-4 shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-4">
          <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest block border-b border-zinc-900 pb-2">
            Slides (12)
          </span>

          <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
            {slides.map((slide) => {
              const isActive = selectedSlide === slide.number;
              return (
                <div
                  key={slide.number}
                  onClick={() => setSelectedSlide(slide.number)}
                  className={`bg-[#070709] border rounded-xl p-3.5 space-y-2 cursor-pointer transition-all ${
                    isActive ? "border-indigo-500 bg-indigo-500/[0.02]" : "border-zinc-900 hover:border-zinc-850"
                  }`}
                >
                  <div className="flex justify-between text-[8px] font-extrabold text-zinc-500 uppercase tracking-wider">
                    <span>Slide {slide.number}</span>
                    {slide.status && <span className="text-purple-400 animate-pulse">{slide.status}</span>}
                  </div>
                  <h4 className="text-xs font-bold text-white tracking-tight leading-snug">{slide.title}</h4>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-medium truncate">
                    {slide.preview}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Column 2 & 3: Selected Slide Editor */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[220px]">
            {/* Editor tools row */}
            <div className="flex items-center gap-3 border-b border-zinc-900 pb-3 mb-6 text-[9.5px] font-bold text-zinc-500 uppercase tracking-wider">
              <span>Text editor</span>
              <span>•</span>
              <span>Layout</span>
              <span>•</span>
              <span>Metrics</span>
            </div>

            {/* Slide active view */}
            <div className="flex-1 flex flex-col justify-center items-center py-6 text-center">
              <h2 className="text-2xl font-black text-white max-w-md leading-snug tracking-tight">
                {selectedSlide === 1 && (
                  <>
                    The Problem: <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-indigo-300">Legacy friction</span> costs B2B $2T annually.
                  </>
                )}
                {selectedSlide === 2 && "The Solution: Instant multi-network settlement engines."}
                {selectedSlide === 3 && "$12.4B Addressable Market Size Opportunity."}
                {selectedSlide === 4 && "Financial Projections: Est. 3x growth by Year 3."}
              </h2>
            </div>
          </div>

          {/* AI Speaker Notes Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-3">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest block border-b border-zinc-900 pb-2">
              AI Generated Speaker Notes
            </span>
            <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
              &ldquo;When we speak to CFOs, their biggest pain point isn&apos;t software—it&apos;s liquidity. By highlighting the $2T tied up in slow settlement, we anchor the problem in an undeniable, massive market inefficiency before introducing our blockchain solution on the next slide.&rdquo;
            </p>
          </div>
        </div>

        {/* Column 4: Pitch Copilot & Sources */}
        <div className="space-y-6">
          {/* Pitch Copilot */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[220px]">
            <div className="space-y-4">
              <span className="text-[9px] font-bold text-white uppercase tracking-widest block border-b border-zinc-900 pb-2 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
                Pitch Copilot
              </span>

              <div className="bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-3.5 text-[10.5px] text-zinc-500 leading-relaxed font-medium">
                I noticed your &quot;Problem&quot; slide is text-heavy. Would you like me to convert those bullet points into an infographic showing money flow bottlenecks?
              </div>
            </div>

            <form onSubmit={handleRefine} className="pt-4 border-t border-zinc-900 mt-4">
              <div className="relative">
                <input
                  type="text"
                  value={copilotInput}
                  onChange={(e) => setCopilotInput(e.target.value)}
                  placeholder="Ask AI to refine this slide..."
                  className="block w-full px-3 py-2 text-[10.5px] text-zinc-300 bg-[#070709] border border-zinc-850 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 rounded-xl outline-none transition-all placeholder:text-zinc-650"
                />
              </div>
            </form>
          </div>

          {/* Linked Data Sources */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <span className="text-[9px] font-bold text-zinc-550 uppercase tracking-widest block border-b border-zinc-900 pb-2 mb-3">
              Linked Data Sources
            </span>

            <div className="space-y-2.5 text-[10.5px] font-semibold text-zinc-400">
              <div className="flex items-center justify-between py-1 border-b border-zinc-900/60 last:border-0">
                <span className="flex items-center gap-2">
                  <Database className="w-3.5 h-3.5 text-zinc-500" />
                  Q3_Financials.csv
                </span>
                <span className="text-[8px] text-zinc-600 font-bold uppercase">CSV</span>
              </div>
              <div className="flex items-center justify-between py-1 border-b border-zinc-900/60 last:border-0">
                <span className="flex items-center gap-2">
                  <Link2 className="w-3.5 h-3.5 text-indigo-400" />
                  Stripe API (Live)
                </span>
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-green-500 shrink-0"></span>
              </div>
              <div className="flex items-center justify-between py-1 border-b border-zinc-900/60 last:border-0">
                <span className="flex items-center gap-2">
                  <FolderOpen className="w-3.5 h-3.5 text-zinc-500 animate-pulse" />
                  Competitor_Data.pdf
                </span>
                <span className="text-[8px] text-zinc-600 font-bold uppercase animate-pulse">Syncing...</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
