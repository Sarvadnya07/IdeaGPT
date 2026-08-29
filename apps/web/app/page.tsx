"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowRight,
  Lightbulb,
  Map,
  Layers,
  Sparkles,
  Shield,
  Cpu,
  Compass,
} from "lucide-react";
import { Show } from "@clerk/nextjs";
import { IdeaGPTLogo } from "../components/brand/IdeaGPTLogo";
import { EvidenceBadge } from "../components/brand/EvidenceBadge";
import { AIStateIndicator } from "../components/brand/AIStateIndicator";
import { StrategyPathwayCard } from "../components/brand/StrategyPathwayCard";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#101012] text-zinc-100 font-sans selection:bg-[#00C29A]/30 overflow-x-hidden relative">
      {/* Background ambient gradient graphics */}
      <div className="absolute top-[-10%] left-[-10%] w-[550px] h-[550px] rounded-full bg-[#00C29A]/5 blur-[140px] pointer-events-none" />
      <div className="absolute top-[20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-[#0284C7]/5 blur-[160px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[20%] w-[500px] h-[500px] rounded-full bg-[#3B82F6]/5 blur-[150px] pointer-events-none" />

      {/* Navigation Header */}
      <header className="sticky top-0 z-40 w-full bg-[#101012]/85 backdrop-blur-md border-b border-zinc-800/60 px-6 sm:px-12 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <Link href="/" className="focus:outline-none">
            <IdeaGPTLogo size="md" variant="full" />
          </Link>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-2 mr-2">
              <AIStateIndicator status="analyzing" label="AI Engine Active" />
            </div>

            <Show when="signed-out">
              <Link
                href="/sign-in"
                className="text-xs font-bold text-zinc-400 hover:text-zinc-200 transition-colors uppercase tracking-wider"
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-zinc-950 bg-[#00C29A] hover:bg-[#00C29A]/90 shadow-[0_0_20px_rgba(0,194,154,0.35)] rounded-xl transition-all active:scale-95"
              >
                Get Started
                <ArrowRight className="w-3.5 h-3.5 stroke-[2.5]" />
              </Link>
            </Show>
            <Show when="signed-in">
              <Link
                href="/dashboard"
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-zinc-950 bg-[#00C29A] hover:bg-[#00C29A]/90 shadow-[0_0_20px_rgba(0,194,154,0.35)] rounded-xl transition-all active:scale-95"
              >
                Open Dashboard
                <ArrowRight className="w-3.5 h-3.5 stroke-[2.5]" />
              </Link>
            </Show>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 flex flex-col justify-center items-center px-6 sm:px-12 py-20 text-center max-w-5xl mx-auto relative z-10">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-[10px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-300 uppercase tracking-widest shadow-inner">
            <span className="w-2 h-2 rounded-full bg-[#00C29A] animate-pulse" />
            <span>IDEA → EVIDENCE → REASONING → DECISION</span>
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl font-black tracking-tight text-white leading-[1.1] max-w-3xl mx-auto">
            Transform Ideas Into{" "}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00C29A] via-[#0284C7] to-[#3B82F6] drop-shadow-[0_2px_20px_rgba(0,194,154,0.3)]">
              Structured Decisions
            </span>
          </h1>

          <p className="text-sm sm:text-base text-zinc-400 max-w-2xl mx-auto leading-relaxed font-medium">
            IdeaGPT autonomously evaluates startup concepts across technical
            feasibility, evidence verification, risk scorecards, and executable
            MVP roadmaps in seconds.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-2 pt-2 pb-2">
            <EvidenceBadge type="FACT" label="Fact Verified" size="sm" />
            <EvidenceBadge type="ESTIMATE" label="Smart Estimate" size="sm" />
            <EvidenceBadge type="INFERENCE" label="AI Inference" size="sm" />
            <EvidenceBadge
              type="RECOMMENDATION"
              label="Action Strategy"
              size="sm"
            />
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Show when="signed-out">
              <Link
                href="/sign-up"
                className="flex items-center justify-center gap-2 w-full sm:w-auto px-7 py-3.5 text-xs font-bold text-zinc-950 bg-gradient-to-r from-[#00C29A] to-[#0284C7] hover:opacity-95 active:scale-[0.98] rounded-xl transition-all shadow-[0_4px_25px_rgba(0,194,154,0.35)]"
              >
                Start Free Evaluation
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/sign-in"
                className="flex items-center justify-center gap-2 w-full sm:w-auto px-7 py-3.5 text-xs font-bold text-zinc-300 bg-[#18181B] border border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700 active:scale-[0.98] rounded-xl transition-all"
              >
                Sign In to Workspace
              </Link>
            </Show>
            <Show when="signed-in">
              <Link
                href="/dashboard"
                className="flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-3.5 text-sm font-bold text-zinc-950 bg-gradient-to-r from-[#00C29A] to-[#0284C7] hover:opacity-95 active:scale-[0.98] rounded-xl transition-all shadow-[0_4px_25px_rgba(0,194,154,0.35)]"
              >
                Open Dashboard Workspace
                <ArrowRight className="w-4 h-4" />
              </Link>
            </Show>
          </div>
        </div>

        {/* Live Strategy Pathway Preview */}
        <div className="w-full mt-16 max-w-4xl text-left">
          <div className="flex items-center justify-between px-2 mb-3">
            <span className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider flex items-center gap-2">
              <Compass className="w-4 h-4 text-[#00C29A]" />
              Structured Evaluation Sample
            </span>
            <div className="flex items-center gap-2">
              <AIStateIndicator status="completed" label="Engine Validated" />
            </div>
          </div>
          <StrategyPathwayCard />
        </div>

        {/* Feature Highlights Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full mt-16">
          <div className="bg-[#18181B] border border-zinc-800/80 rounded-2xl p-6 text-left relative overflow-hidden group hover:border-zinc-700 transition-all shadow-lg">
            <div className="absolute top-0 right-0 w-[90px] h-[90px] bg-[#00C29A]/5 blur-[30px] pointer-events-none" />
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-[#00C29A]/10 text-[#00C29A] border border-[#00C29A]/20">
              <Lightbulb className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mt-4">
              AI Idea Analysis
            </h3>
            <p className="text-[11px] text-zinc-400 leading-relaxed font-medium mt-2">
              Evaluates market viability, complexity scores, and timeline
              estimations with multi-agent reasoning.
            </p>
          </div>

          <div className="bg-[#18181B] border border-zinc-800/80 rounded-2xl p-6 text-left relative overflow-hidden group hover:border-zinc-700 transition-all shadow-lg">
            <div className="absolute top-0 right-0 w-[90px] h-[90px] bg-[#0284C7]/5 blur-[30px] pointer-events-none" />
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-[#0284C7]/10 text-[#0284C7] border border-[#0284C7]/20">
              <Map className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mt-4">
              Visual Roadmaps
            </h3>
            <p className="text-[11px] text-zinc-400 leading-relaxed font-medium mt-2">
              Generates chronological sprint milestones, resource requirements,
              and risk mitigation paths.
            </p>
          </div>

          <div className="bg-[#18181B] border border-zinc-800/80 rounded-2xl p-6 text-left relative overflow-hidden group hover:border-zinc-700 transition-all shadow-lg">
            <div className="absolute top-0 right-0 w-[90px] h-[90px] bg-[#3B82F6]/5 blur-[30px] pointer-events-none" />
            <div className="flex items-center justify-center w-9 h-9 rounded-xl bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/20">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mt-4">
              Architecture Stacks
            </h3>
            <p className="text-[11px] text-zinc-400 leading-relaxed font-medium mt-2">
              Architects production cloud configurations, database schemas, and
              API gateway routing blueprints.
            </p>
          </div>
        </div>
      </section>

      {/* Landing Footer */}
      <footer className="w-full bg-[#18181B] border-t border-zinc-800/80 px-6 sm:px-12 py-8 mt-auto text-center text-xs text-zinc-500 relative z-10">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <IdeaGPTLogo size="sm" variant="compact" />
            <span>
              &copy; {new Date().getFullYear()} IdeaGPT. Structured
              Decision-Making & Intelligent Transformation.
            </span>
          </div>
          <div className="flex items-center gap-6 font-medium text-zinc-400">
            <Link
              href="/dashboard"
              className="hover:text-white transition-colors"
            >
              Workspace
            </Link>
            <Link
              href="/ai-analysis"
              className="hover:text-white transition-colors"
            >
              Idea Analysis
            </Link>
            <Link
              href="/roadmap"
              className="hover:text-white transition-colors"
            >
              Roadmaps
            </Link>
            <Link
              href="/architecture"
              className="hover:text-white transition-colors"
            >
              Architecture
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
