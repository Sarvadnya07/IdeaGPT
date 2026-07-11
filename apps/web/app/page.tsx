"use client";

import React from "react";
import Link from "next/link";
import { Sparkles, ArrowRight, Lightbulb, Map, Layers, Target } from "lucide-react";
import { Show } from "@clerk/nextjs";
import { Search } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#070709] text-zinc-100 font-sans selection:bg-indigo-500/30 overflow-x-hidden relative">
      {/* Background neon blur graphics */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-600/5 blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-purple-600/5 blur-[150px] pointer-events-none"></div>

      {/* Navigation Header */}
      <header className="sticky top-0 z-40 w-full bg-[#070709]/80 backdrop-blur-md border-b border-zinc-900/60 px-6 sm:px-12 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8.5 h-8.5 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 shadow-[0_0_15px_rgba(79,70,229,0.3)] shrink-0">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="font-extrabold text-base tracking-tight text-white select-none">
              IdeaGPT
            </span>
          </div>

          <div className="flex items-center gap-4">
            <Show when="signed-out">
              <Link
                href="/sign-in"
                className="text-xs font-bold text-zinc-400 hover:text-zinc-200 transition-colors uppercase tracking-wider"
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.3)] rounded-full transition-all active:scale-95"
              >
                Get Started
              </Link>
            </Show>
            <Show when="signed-in">
              <Link
                href="/dashboard"
                className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.3)] rounded-full transition-all active:scale-95"
              >
                Dashboard
              </Link>
            </Show>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1 flex flex-col justify-center items-center px-6 sm:px-12 py-20 text-center max-w-5xl mx-auto relative z-10">
        <div className="space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase tracking-widest animate-pulse">
            <Sparkles className="w-3.5 h-3.5" />
            Empowered by Advanced Reasoning AI
          </div>

          <h1 className="text-5xl sm:text-6xl md:text-7xl font-black tracking-tight text-white leading-[1.1] max-w-3xl mx-auto">
            Validate Concepts{" "}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 drop-shadow-[0_2px_15px_rgba(168,85,247,0.25)]">
              Instantly
            </span>
          </h1>

          <p className="text-sm sm:text-base text-zinc-500 max-w-2xl mx-auto leading-relaxed font-medium">
            IdeaGPT completely analyzes your startup ideas across technical feasibility, target timelines, key risk parameters, and dev pipeline scope in seconds.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Show when="signed-out">
              <Link
                href="/sign-up"
                className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 text-xs font-bold text-white bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 hover:from-indigo-400 hover:to-purple-500 active:scale-[0.98] rounded-xl transition-all shadow-[0_4px_20px_rgba(99,102,241,0.3)]"
              >
                Start Free Evaluation
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/sign-in"
                className="flex items-center justify-center gap-2 w-full sm:w-auto px-6 py-3 text-xs font-bold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700 active:scale-[0.98] rounded-xl transition-all"
              >
                Sign In to Workspace
              </Link>
            </Show>
            <Show when="signed-in">
              <Link
                href="/dashboard"
                className="flex items-center justify-center gap-2 w-full sm:w-auto px-8 py-3 text-sm font-bold text-white bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 hover:from-indigo-400 hover:to-purple-500 active:scale-[0.98] rounded-xl transition-all shadow-[0_4px_20px_rgba(99,102,241,0.3)]"
              >
                Open Dashboard Workspace
                <ArrowRight className="w-4 h-4" />
              </Link>
            </Show>
          </div>
        </div>

        {/* Feature Cards Showcase */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full mt-24">
          {/* Card 1 */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 text-left relative overflow-hidden group hover:border-zinc-800 transition-all">
            <div className="absolute top-0 right-0 w-[80px] h-[80px] bg-indigo-500/5 blur-[30px] pointer-events-none"></div>
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Lightbulb className="w-4.5 h-4.5" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mt-4">
              AI Idea Analysis
            </h3>
            <p className="text-[11px] text-zinc-500 leading-relaxed font-medium mt-2">
              Evaluates tech complexity, Time to MVP, and dynamic startup potential values automatically.
            </p>
          </div>

          {/* Card 2 */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 text-left relative overflow-hidden group hover:border-zinc-800 transition-all">
            <div className="absolute top-0 right-0 w-[80px] h-[80px] bg-purple-500/5 blur-[30px] pointer-events-none"></div>
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-purple-500/10 text-purple-400">
              <Map className="w-4.5 h-4.5" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mt-4">
              Visual Roadmaps
            </h3>
            <p className="text-[11px] text-zinc-500 leading-relaxed font-medium mt-2">
              Generates chronological milestones, MVP scopes, priority checklists, and key risks data.
            </p>
          </div>

          {/* Card 3 */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 text-left relative overflow-hidden group hover:border-zinc-800 transition-all">
            <div className="absolute top-0 right-0 w-[80px] h-[80px] bg-emerald-500/5 blur-[30px] pointer-events-none"></div>
            <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Layers className="w-4.5 h-4.5" />
            </div>
            <h3 className="text-sm font-bold text-white uppercase tracking-wider mt-4">
              Architecture Stacks
            </h3>
            <p className="text-[11px] text-zinc-500 leading-relaxed font-medium mt-2">
              Recommends complete edge backend structures, database vectors, and DevOps pipelines.
            </p>
          </div>
        </div>
      </section>

      {/* Landing Footer */}
      <footer className="w-full bg-[#09090b] border-t border-zinc-900 px-6 sm:px-12 py-8 mt-auto text-center text-xs text-zinc-600 relative z-10">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-extrabold text-sm text-zinc-500 tracking-tight mr-2">
              IdeaGPT
            </span>
            &copy; {new Date().getFullYear()} IdeaGPT AI. All rights reserved.
          </div>
          <div className="flex items-center gap-6 font-medium">
            <Link href="#" className="hover:text-zinc-400 transition-colors">
              Product
            </Link>
            <Link href="#" className="hover:text-zinc-400 transition-colors">
              API
            </Link>
            <Link href="#" className="hover:text-zinc-400 transition-colors">
              Privacy
            </Link>
            <Link href="#" className="hover:text-zinc-400 transition-colors">
              Terms
            </Link>
            <Link href="#" className="hover:text-zinc-400 transition-colors">
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
