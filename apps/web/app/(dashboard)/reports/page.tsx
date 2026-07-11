"use client";

import React from "react";
import Link from "next/link";
import { useIdea } from "../../providers";
import { Bookmark, Sparkles, ArrowRight, Star, Share2 } from "lucide-react";
import { toast } from "sonner";

interface SavedReport {
  title: string;
  industry: string;
  score: number;
  timeline: string;
  date: string;
  description: string;
}

export default function ReportsPage() {
  const { idea } = useIdea();

  const savedReports: SavedReport[] = [
    {
      title: idea.title,
      industry: idea.industry,
      score: idea.potential,
      timeline: idea.timeline,
      date: "Today",
      description: idea.problem.substring(0, 100) + "...",
    },
    {
      title: "Decentralized Credit Registry",
      industry: "DeFi / Web3",
      score: 84,
      timeline: "6-12 Mo",
      date: "May 18, 2026",
      description: "A secure protocol using zero-knowledge proofs to register cross-border corporate credit profiles.",
    },
    {
      title: "Omni-Channel Customer Support Bot",
      industry: "AI / SaaS",
      score: 91,
      timeline: "1-3 Mo",
      date: "Apr 29, 2026",
      description: "Generative customer support system that auto-trains on custom PDF documentation repositories.",
    },
  ];

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Title */}
      <div className="space-y-2 border-b border-zinc-900 pb-6">
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Saved Reports
        </h1>
        <p className="text-sm text-zinc-500 leading-relaxed">
          Access your library of past AI valuations, technical stack generation files, and timeline roadmaps.
        </p>
      </div>

      {/* Reports List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-5xl">
        {savedReports.map((report, idx) => (
          <div
            key={idx}
            className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] hover:border-zinc-800 transition-all flex flex-col justify-between min-h-[190px] relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 w-[120px] h-[120px] bg-zinc-800/[0.02] group-hover:bg-zinc-800/[0.04] blur-[40px] pointer-events-none"></div>

            <div className="space-y-3">
              <div className="flex items-center justify-between gap-4">
                <span className="inline-block px-2 py-0.5 rounded text-[8px] font-bold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 uppercase tracking-widest">
                  {report.industry}
                </span>
                <span className="text-[10px] text-zinc-500 font-semibold flex items-center gap-1">
                  <Star className="w-3.5 h-3.5 text-zinc-500 fill-zinc-500" />
                  Score: {report.score}
                </span>
              </div>

              <h3 className="text-base font-extrabold text-white">
                {report.title}
              </h3>
              <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
                {report.description}
              </p>
            </div>

            <div className="flex items-center justify-between border-t border-zinc-900/60 pt-4 mt-4">
              <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-wider">
                {report.date}
              </span>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toast.success("Shared Link copied to clipboard!")}
                  className="p-2 rounded-lg text-zinc-500 hover:text-zinc-300 hover:bg-[#121214] transition-colors"
                >
                  <Share2 className="w-3.5 h-3.5" />
                </button>
                <Link
                  href="/ai-analysis"
                  className="flex items-center gap-1.5 text-[10px] font-bold text-indigo-400 hover:text-indigo-300 transition-colors uppercase tracking-wider"
                >
                  Open Report
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
