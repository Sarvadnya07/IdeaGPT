"use client";

import React from "react";
import Link from "next/link";
import {
  ArrowRight,
  Play,
  Eye,
  Shield,
  Target,
  GitFork,
  Sliders,
  FolderLock,
  Lock,
  Compass,
  BarChart3,
  Users2,
  ShieldAlert,
  Lightbulb,
  Map,
  Layers,
  Cpu,
  FileText,
  Presentation,
  FileCheck,
  GitCompare,
  ChevronDown,
  Sparkles,
} from "lucide-react";
import { Show } from "@clerk/nextjs";
import { IdeaGPTLogo } from "../components/brand/IdeaGPTLogo";
import { LandingHeader } from "../components/landing/LandingHeader";
import { HeroIntelligenceCard } from "../components/landing/HeroIntelligenceCard";
import { InteractiveActionDemo } from "../components/landing/InteractiveActionDemo";
import { LandingTechStack } from "../components/landing/LandingTechStack";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-[#070709] text-zinc-100 font-sans selection:bg-[#00C29A]/30 overflow-x-hidden relative">
      {/* Top Announcement Banner */}
      <div className="w-full bg-[#0B0B0E] border-b border-zinc-800/60 py-2 px-4 text-center z-50">
        <div className="max-w-7xl mx-auto flex items-center justify-center gap-2 text-[11px] sm:text-xs text-zinc-300">
          <span className="inline-block w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span className="font-mono font-bold text-emerald-400 uppercase tracking-wider">
            SYSTEM UPDATE:
          </span>
          <span className="text-zinc-300">
            Decision Engine v2.4 is live. Enhanced context retention and research accuracy.
          </span>
          <Link
            href="/dashboard"
            className="text-emerald-400 hover:text-emerald-300 font-bold ml-1 inline-flex items-center gap-0.5 hover:underline"
          >
            Learn more &rarr;
          </Link>
        </div>
      </div>

      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/4 w-[600px] h-[600px] rounded-full bg-[#00C29A]/5 blur-[160px] pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-[600px] h-[600px] rounded-full bg-[#0284C7]/5 blur-[180px] pointer-events-none" />
      <div className="absolute bottom-1/4 left-10 w-[500px] h-[500px] rounded-full bg-[#3B82F6]/5 blur-[160px] pointer-events-none" />

      {/* Navigation Header */}
      <LandingHeader />

      {/* Hero Section (2-Column Grid) */}
      <section className="w-full max-w-7xl mx-auto px-6 sm:px-12 pt-14 pb-16 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-center">
          {/* Left Column */}
          <div className="lg:col-span-6 space-y-6 text-left">
            {/* Tag Pill */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-[10px] font-mono font-bold bg-[#111115] border border-zinc-800 text-zinc-300 tracking-wider shadow-inner">
              <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF]" />
              <span>IDEA &rarr; EVIDENCE &rarr; REASONING &rarr; DECISION</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1]">
              Transform Ideas Into{" "}
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00E5FF] to-[#3B82F6]">
                Structured Decisions.
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-sm sm:text-base text-zinc-400 leading-relaxed font-normal max-w-xl">
              IdeaGPT evaluates startup concepts using evidence-backed research, multi-agent reasoning, and deterministic evaluation to convert raw ideas into actionable intelligence.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Show when="signed-out">
                <Link
                  href="/sign-up"
                  className="flex items-center gap-2 px-6 py-3 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_25px_rgba(0,229,255,0.4)] rounded-xl transition-all active:scale-95"
                >
                  <Play className="w-3.5 h-3.5 fill-zinc-950" />
                  <span>Start Free</span>
                </Link>
                <Link
                  href="#how-it-works"
                  className="flex items-center gap-2 px-5 py-3 text-xs font-semibold text-zinc-300 bg-[#141418] border border-zinc-800 hover:bg-zinc-800 hover:text-white rounded-xl transition-all"
                >
                  <Eye className="w-4 h-4 text-zinc-400" />
                  <span>See How It Works</span>
                </Link>
              </Show>
              <Show when="signed-in">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 px-7 py-3 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_25px_rgba(0,229,255,0.4)] rounded-xl transition-all active:scale-95"
                >
                  <Play className="w-3.5 h-3.5 fill-zinc-950" />
                  <span>Go to Workspace</span>
                </Link>
              </Show>
            </div>

            {/* Intelligence Taxonomy Badges */}
            <div className="pt-4 border-t border-zinc-800/60 space-y-2">
              <div className="text-[10px] font-mono font-bold tracking-widest text-zinc-500 uppercase">
                INTELLIGENCE TAXONOMY
              </div>
              <div className="flex flex-wrap items-center gap-2.5">
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#00E5FF]/10 border border-[#00E5FF]/30 text-[#00E5FF] text-[10px] font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#00E5FF]" />
                  <span>FACT</span>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-500/10 border border-amber-500/30 text-amber-300 text-[10px] font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                  <span>ESTIMATE</span>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-500/10 border border-blue-500/30 text-blue-300 text-[10px] font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                  <span>INFERENCE</span>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-purple-500/10 border border-purple-500/30 text-purple-300 text-[10px] font-bold">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400" />
                  <span>RECOMMENDATION</span>
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: AI Decision Intelligence Card */}
          <div className="lg:col-span-6 h-full min-h-[380px]">
            <HeroIntelligenceCard />
          </div>
        </div>
      </section>

      {/* 6 Value Pillars Row */}
      <section className="w-full max-w-7xl mx-auto px-6 sm:px-12 py-8">
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
          {[
            {
              title: "Evidence-Backed",
              desc: "We show you what's verified, estimated, inferred, or unknown.",
              icon: Shield,
              color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
            },
            {
              title: "Multi-Agent Reasoning",
              desc: "Specialized agents analyze, challenge assumptions, and synthesize insights.",
              icon: Target,
              color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
            },
            {
              title: "Deterministic Scoring",
              desc: "Transparent scoring models you can trust and reproduce.",
              icon: GitFork,
              color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
            },
            {
              title: "Decision Frameworks",
              desc: "From GO / PIVOT / VALIDATE to execution-ready recommendations.",
              icon: Sliders,
              color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
            },
            {
              title: "Actionable Outputs",
              desc: "Roadmaps, PRDs, architecture, pitch decks, and investor reports.",
              icon: FolderLock,
              color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
            },
            {
              title: "Your Data. Your Control.",
              desc: "Secure, private, and never used to train external models.",
              icon: Lock,
              color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
            },
          ].map((pillar) => {
            const Icon = pillar.icon;
            return (
              <div
                key={pillar.title}
                className="bg-[#0D0D10] border border-zinc-800/80 rounded-xl p-4 flex flex-col justify-between hover:border-zinc-700 transition-all group shadow-md"
              >
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center border mb-3 ${pillar.color} group-hover:scale-105 transition-transform`}
                >
                  <Icon className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-white tracking-tight">
                    {pillar.title}
                  </h3>
                  <p className="text-[11px] text-zinc-400 leading-snug mt-1.5 font-normal">
                    {pillar.desc}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Interactive Action Demo Stepper Section */}
      <div id="how-it-works">
        <InteractiveActionDemo />
      </div>

      {/* "Why Founders Choose IdeaGPT" 6 Big Metric Cards */}
      <section className="w-full max-w-7xl mx-auto px-6 sm:px-12 py-16 text-center">
        <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-10">
          Why Founders Choose{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00E5FF] to-[#3B82F6]">
            IdeaGPT
          </span>
        </h2>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3.5">
          {[
            {
              stat: "10x",
              title: "Faster Evaluation",
              desc: "From days of research to minutes of clarity.",
              statColor: "text-[#00E5FF]",
            },
            {
              stat: "128+",
              title: "Data Sources",
              desc: "Real-time web research with source citations.",
              statColor: "text-white",
            },
            {
              stat: "6",
              title: "Specialized Agents",
              desc: "Each expert agent validates and challenges ideas.",
              statColor: "text-[#3B82F6]",
            },
            {
              stat: "94%",
              title: "Confidence Score",
              desc: "Transparent confidence for every insight.",
              statColor: "text-purple-400",
            },
            {
              stat: "Zero",
              title: "Black Box",
              desc: "Full visibility into models, providers, and reasoning.",
              statColor: "text-emerald-400",
            },
            {
              stat: "100%",
              title: "Your Data",
              desc: "Your ideas remain private and fully encrypted.",
              statColor: "text-[#00E5FF]",
            },
          ].map((item) => (
            <div
              key={item.title}
              className="bg-[#0D0D10] border border-zinc-800/80 rounded-xl p-5 text-left flex flex-col justify-between hover:border-zinc-700 transition-all shadow-md group"
            >
              <div
                className={`text-3xl sm:text-4xl font-black tracking-tight ${item.statColor} group-hover:scale-105 transition-transform`}
              >
                {item.stat}
              </div>
              <div className="mt-4">
                <div className="text-xs font-bold text-white tracking-tight">
                  {item.title}
                </div>
                <p className="text-[11px] text-zinc-400 mt-1 leading-snug">
                  {item.desc}
                </p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* "Everything You Need to Go From Idea to Execution" 12 Feature Cards */}
      <section id="capabilities" className="w-full max-w-7xl mx-auto px-6 sm:px-12 py-16 text-center">
        <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white mb-10">
          Everything You Need to Go{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00E5FF] to-[#3B82F6]">
            From Idea to Execution
          </span>
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-left">
          {[
            {
              title: "Idea Evaluation",
              desc: "Score feasibility, market potential, risk, and execution complexity.",
              icon: Compass,
              color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
              href: "/ai-analysis",
            },
            {
              title: "Market Research",
              desc: "Real-time market size, trends, and industry landscape.",
              icon: BarChart3,
              color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
              href: "/ai-analysis",
            },
            {
              title: "Competitor Analysis",
              desc: "Deep competitor profiling and differentiation mapping.",
              icon: Users2,
              color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
              href: "/ai-analysis",
            },
            {
              title: "Risk Analysis",
              desc: "Technical, market, financial, and regulatory risk assessment.",
              icon: ShieldAlert,
              color: "text-red-400 bg-red-500/10 border-red-500/20",
              href: "/ai-analysis",
            },
            {
              title: "Strategy Lab",
              desc: "Scenario planning, sensitivity analysis, and decision frameworks.",
              icon: Lightbulb,
              color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
              href: "/strategy-lab",
            },
            {
              title: "Roadmaps",
              desc: "Chronological milestones with effort, dependencies, and priorities.",
              icon: Map,
              color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
              href: "/roadmap",
            },
            {
              title: "Architecture",
              desc: "System architecture, data models, and technical blueprints.",
              icon: Layers,
              color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
              href: "/architecture",
            },
            {
              title: "Tech Stack",
              desc: "Best-fit stack recommendations with trade-off analysis.",
              icon: Cpu,
              color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
              href: "/tech-stack",
            },
            {
              title: "PRD Generator",
              desc: "AI-written PRDs with features, user stories, and acceptance criteria.",
              icon: FileText,
              color: "text-green-400 bg-green-500/10 border-green-500/20",
              href: "/prd-generator",
            },
            {
              title: "Pitch Deck",
              desc: "Investor-ready pitch decks with market and financials.",
              icon: Presentation,
              color: "text-rose-400 bg-rose-500/10 border-rose-500/20",
              href: "/pitch-deck",
            },
            {
              title: "Reports",
              desc: "Executive summaries, full reports, and downloadable exports.",
              icon: FileCheck,
              color: "text-sky-400 bg-sky-500/10 border-sky-500/20",
              href: "/reports",
            },
            {
              title: "Compare Ideas",
              desc: "Compare multiple ideas side-by-side and pick the best one.",
              icon: GitCompare,
              color: "text-yellow-400 bg-yellow-500/10 border-yellow-500/20",
              href: "/compare",
            },
          ].map((card) => {
            const Icon = card.icon;
            return (
              <Link
                key={card.title}
                href={card.href}
                className="bg-[#0D0D10] border border-zinc-800/80 rounded-xl p-5 flex flex-col justify-between hover:border-zinc-700 hover:bg-[#121216] transition-all group shadow-md"
              >
                <div
                  className={`w-9 h-9 rounded-lg flex items-center justify-center border mb-4 ${card.color} group-hover:scale-105 transition-transform`}
                >
                  <Icon className="w-4.5 h-4.5" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-white tracking-tight flex items-center justify-between">
                    <span>{card.title}</span>
                    <ArrowRight className="w-3 h-3 text-zinc-600 group-hover:text-zinc-300 transition-colors opacity-0 group-hover:opacity-100" />
                  </h3>
                  <p className="text-[11px] text-zinc-400 mt-1.5 leading-relaxed">
                    {card.desc}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* Tech Stack Banner */}
      <LandingTechStack />

      {/* Bottom Large CTA Card / Pricing Tier Anchor */}
      <section id="pricing" className="w-full max-w-7xl mx-auto px-6 sm:px-12 py-12">
        <div className="rounded-2xl bg-gradient-to-r from-[#0C0C10] via-[#0E1520] to-[#0A1A1E] border border-zinc-800 p-8 sm:p-12 relative overflow-hidden shadow-2xl flex flex-col md:flex-row items-center justify-between gap-8">
          {/* Background glow effects */}
          <div className="absolute right-0 top-0 w-96 h-96 bg-[#00E5FF]/10 rounded-full blur-3xl pointer-events-none" />

          {/* Left Text & Actions */}
          <div className="space-y-4 max-w-xl text-left relative z-10">
            <h2 className="text-3xl sm:text-4xl font-black tracking-tight text-white">
              Stop Guessing. Start Deciding.
            </h2>
            <p className="text-xs sm:text-sm text-zinc-400">
              Join founders who turn uncertainty into clarity.
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <Show when="signed-out">
                <Link
                  href="/sign-up"
                  className="flex items-center gap-2 px-6 py-3 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_20px_rgba(0,229,255,0.4)] rounded-xl transition-all active:scale-95"
                >
                  <Play className="w-3.5 h-3.5 fill-zinc-950" />
                  <span>Start Free</span>
                </Link>
                <Link
                  href="#how-it-works"
                  className="flex items-center gap-2 px-5 py-3 text-xs font-semibold text-zinc-300 bg-[#141418] border border-zinc-800 hover:bg-zinc-800 hover:text-white rounded-xl transition-all"
                >
                  <Eye className="w-4 h-4 text-zinc-400" />
                  <span>See How It Works</span>
                </Link>
              </Show>
              <Show when="signed-in">
                <Link
                  href="/dashboard"
                  className="flex items-center gap-2 px-7 py-3 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_20px_rgba(0,229,255,0.4)] rounded-xl transition-all active:scale-95"
                >
                  <Play className="w-3.5 h-3.5 fill-zinc-950" />
                  <span>Open Dashboard</span>
                </Link>
              </Show>
            </div>
          </div>

          {/* Right 3D Cube / Visual Graphic */}
          <div className="relative z-10 w-44 h-44 sm:w-52 sm:h-52 shrink-0 flex items-center justify-center">
            <svg
              viewBox="0 0 200 200"
              className="w-full h-full drop-shadow-[0_0_35px_rgba(0,229,255,0.35)]"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <defs>
                <linearGradient id="cubeTop" x1="50" y1="20" x2="150" y2="70" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#00E5FF" />
                  <stop offset="100%" stopColor="#00C29A" />
                </linearGradient>
                <linearGradient id="cubeLeft" x1="30" y1="60" x2="100" y2="150" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#0284C7" />
                  <stop offset="100%" stopColor="#1E3A8A" />
                </linearGradient>
                <linearGradient id="cubeRight" x1="100" y1="60" x2="170" y2="150" gradientUnits="userSpaceOnUse">
                  <stop offset="0%" stopColor="#00C29A" />
                  <stop offset="100%" stopColor="#0F766E" />
                </linearGradient>
              </defs>

              {/* Holographic Circuit Base */}
              <ellipse cx="100" cy="155" rx="80" ry="25" fill="#00E5FF" fillOpacity="0.08" />
              <ellipse cx="100" cy="155" rx="55" ry="16" stroke="#00E5FF" strokeOpacity="0.3" strokeDasharray="4 4" />

              {/* 3D Isometric Cube / Core */}
              <g transform="translate(0, -10)">
                {/* Top face */}
                <polygon points="100,30 160,65 100,100 40,65" fill="url(#cubeTop)" />
                {/* Left face */}
                <polygon points="40,65 100,100 100,165 40,130" fill="url(#cubeLeft)" />
                {/* Right face */}
                <polygon points="100,100 160,65 160,130 100,165" fill="url(#cubeRight)" />

                {/* Inner glowing symbol / decision notch */}
                <polygon points="100,50 135,70 100,90 65,70" fill="#070709" fillOpacity="0.4" />
                <circle cx="100" cy="70" r="6" fill="#FFFFFF" />
              </g>
            </svg>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="w-full bg-[#060608] border-t border-zinc-800/80 px-6 sm:px-12 py-12 text-xs text-zinc-500 relative z-10">
        <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-8">
          {/* Brand Info */}
          <div className="md:col-span-2 space-y-3 text-left">
            <IdeaGPTLogo size="sm" variant="compact" showSubtitle={false} />
            <p className="text-zinc-400 text-xs leading-relaxed max-w-sm">
              &copy; {new Date().getFullYear()} IdeaGPT. Technical Intelligence for High-Stakes Strategy.
            </p>
            <div className="flex items-center gap-3 pt-2 text-zinc-400">
              <Link href="#" className="hover:text-[#00E5FF] transition-colors">
                Twitter
              </Link>
              <Link href="#" className="hover:text-[#00E5FF] transition-colors">
                LinkedIn
              </Link>
              <Link href="#" className="hover:text-[#00E5FF] transition-colors">
                GitHub
              </Link>
            </div>
          </div>

          {/* Links Columns */}
          <div className="space-y-2.5 text-left">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Product
            </h4>
            <div className="flex flex-col space-y-1.5 text-zinc-400">
              <Link href="/dashboard" className="hover:text-white transition-colors">
                Overview
              </Link>
              <Link href="#pricing" className="hover:text-white transition-colors">
                Pricing
              </Link>
              <Link href="#updates" className="hover:text-white transition-colors">
                Updates
              </Link>
            </div>
          </div>

          <div className="space-y-2.5 text-left">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Resources
            </h4>
            <div className="flex flex-col space-y-1.5 text-zinc-400">
              <Link href="/docs" className="hover:text-white transition-colors">
                Documentation
              </Link>
              <Link href="/api-docs" className="hover:text-white transition-colors">
                API Reference
              </Link>
              <Link href="/guides" className="hover:text-white transition-colors">
                Guides
              </Link>
            </div>
          </div>

          <div className="space-y-2.5 text-left">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">
              Legal
            </h4>
            <div className="flex flex-col space-y-1.5 text-zinc-400">
              <Link href="/terms" className="hover:text-white transition-colors">
                Terms of Service
              </Link>
              <Link href="/privacy" className="hover:text-white transition-colors">
                Privacy Policy
              </Link>
              <Link href="/security" className="hover:text-white transition-colors">
                Security
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
