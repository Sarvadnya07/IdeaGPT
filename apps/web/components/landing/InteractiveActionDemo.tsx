"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Sparkles,
  Lightbulb,
  Search,
  FileCheck2,
  GitBranch,
  ShieldCheck,
  CheckCircle2,
  Compass,
} from "lucide-react";

interface ExampleIdea {
  title: string;
  query: string;
  stepDetails: string[];
  decision: string;
  decisionColor: string;
  nextStep: string;
}

const examples: ExampleIdea[] = [
  {
    title: "AI Copilot for SMBs",
    query: "AI Copilot for SMB invoice processing & cashflow forecasting",
    stepDetails: [
      "Raw concept input",
      "Feasibility 9.2/10",
      "24 Competitors identified",
      "142 Data sources verified",
      "Trade-offs & margin models",
      "Recommendation & roadmap",
    ],
    decision: "GO / ACCELERATE",
    decisionColor: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
    nextStep: "Launch closed beta with 10 design partners",
  },
  {
    title: "Personal Safety Platform",
    query: "AI-powered personal safety platform with predictive threat analysis",
    stepDetails: [
      "Raw concept input",
      "Feasibility & viability",
      "Market & competitors",
      "Sources & validation",
      "Trade-offs & risk analysis",
      "Recommendation & next steps",
    ],
    decision: "VALIDATE FIRST",
    decisionColor: "text-amber-400 bg-amber-500/10 border-amber-500/30",
    nextStep: "Run market validation and user interviews",
  },
  {
    title: "DevTool for APIs",
    query: "Autonomous schema drift detection and auto-healing API gateways",
    stepDetails: [
      "Raw developer pain point",
      "Technical viability 9.5/10",
      "Enterprise developer TAM",
      "89 Architecture references",
      "Compute cost sensitivity",
      "Phase 1 MVP architecture",
    ],
    decision: "BUILD PROTOTYPE",
    decisionColor: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30",
    nextStep: "Implement core eBPF agent monitoring harness",
  },
];

export function InteractiveActionDemo() {
  const [selectedExample, setSelectedExample] = useState<number>(1);
  const [inputValue, setInputValue] = useState(examples[1].query);
  const [activeStep, setActiveStep] = useState<number>(5);

  const handleSelectExample = (idx: number) => {
    setSelectedExample(idx);
    setInputValue(examples[idx].query);
  };

  const current = examples[selectedExample];

  const steps = [
    { num: 1, name: "IDEA", sub: current.stepDetails[0], icon: Lightbulb, color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30" },
    { num: 2, name: "EVALUATE", sub: current.stepDetails[1], icon: Compass, color: "text-teal-400 bg-teal-500/10 border-teal-500/30" },
    { num: 3, name: "RESEARCH", sub: current.stepDetails[2], icon: Search, color: "text-sky-400 bg-sky-500/10 border-sky-500/30" },
    { num: 4, name: "EVIDENCE", sub: current.stepDetails[3], icon: FileCheck2, color: "text-blue-400 bg-blue-500/10 border-blue-500/30" },
    { num: 5, name: "REASON", sub: current.stepDetails[4], icon: GitBranch, color: "text-indigo-400 bg-indigo-500/10 border-indigo-500/30" },
    { num: 6, name: "DECIDE", sub: current.stepDetails[5], icon: ShieldCheck, color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30" },
  ];

  return (
    <section className="w-full py-16 px-4 sm:px-8 max-w-7xl mx-auto">
      {/* Section Header */}
      <div className="text-center mb-10">
        <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-white">
          See IdeaGPT In{" "}
          <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00C29A] via-[#00E5FF] to-[#3B82F6]">
            Action
          </span>
        </h2>
        <p className="text-sm text-zinc-400 mt-2.5 max-w-xl mx-auto">
          Enter your startup idea and watch it transform into structured decision intelligence.
        </p>
      </div>

      {/* Interactive Flow Container */}
      <div className="rounded-2xl bg-[#0D0D10] border border-zinc-800/90 p-5 sm:p-7 shadow-[0_12px_40px_rgba(0,0,0,0.7)] relative overflow-hidden">
        {/* Ambient background glow */}
        <div className="absolute -top-24 -left-24 w-72 h-72 bg-[#00C29A]/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-24 -right-24 w-72 h-72 bg-[#3B82F6]/10 rounded-full blur-3xl pointer-events-none" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center relative z-10">
          {/* Left Column: Input Form & Examples */}
          <div className="lg:col-span-4 space-y-4">
            <div className="relative">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Enter startup idea..."
                className="w-full px-4 py-3.5 pr-28 rounded-xl bg-[#141418] border border-zinc-700/80 text-xs sm:text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-[#00C29A] focus:ring-1 focus:ring-[#00C29A] transition-all shadow-inner"
              />
              <Link
                href={`/ai-analysis?idea=${encodeURIComponent(inputValue)}`}
                className="absolute right-1.5 top-1.5 bottom-1.5 px-3 rounded-lg bg-[#00C29A] hover:bg-[#00C29A]/90 text-zinc-950 text-xs font-bold flex items-center gap-1 shadow-md transition-all active:scale-95"
              >
                <span>Analyze</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            {/* Example pills */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
              <span className="text-[11px] font-semibold text-zinc-400">
                Try example:
              </span>
              {examples.map((ex, idx) => (
                <button
                  key={ex.title}
                  onClick={() => handleSelectExample(idx)}
                  className={`px-2.5 py-1 rounded-md text-[11px] font-medium transition-all ${
                    selectedExample === idx
                      ? "bg-[#00C29A]/15 text-[#00C29A] border border-[#00C29A]/40 font-bold"
                      : "bg-[#141418] text-zinc-400 hover:text-zinc-200 border border-zinc-800 hover:border-zinc-700"
                  }`}
                >
                  {ex.title}
                </button>
              ))}
            </div>
          </div>

          {/* Right Column: 6-Step Pipeline & Decision Card */}
          <div className="lg:col-span-8 grid grid-cols-1 md:grid-cols-12 gap-4 items-center">
            {/* 6 Stepper nodes */}
            <div className="md:col-span-8 grid grid-cols-3 sm:grid-cols-6 gap-2 sm:gap-2.5">
              {steps.map((st, i) => {
                const Icon = st.icon;
                const isSelected = activeStep === i;
                return (
                  <div
                    key={st.name}
                    onClick={() => setActiveStep(i)}
                    className={`flex flex-col items-center text-center p-2.5 rounded-xl border transition-all cursor-pointer group ${
                      isSelected
                        ? "bg-[#141418] border-zinc-600 shadow-[0_0_15px_rgba(0,194,154,0.15)]"
                        : "bg-[#111115]/80 border-zinc-800/80 hover:border-zinc-700 hover:bg-[#141418]"
                    }`}
                  >
                    <div
                      className={`w-7 h-7 rounded-lg flex items-center justify-center border mb-1.5 transition-all ${st.color} group-hover:scale-105`}
                    >
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-[9px] font-mono font-black tracking-wider text-white">
                      {st.num} {st.name}
                    </span>
                    <span className="text-[8px] text-zinc-400 leading-tight mt-0.5 line-clamp-2">
                      {st.sub}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* End State Decision Output Card */}
            <div className="md:col-span-4 rounded-xl bg-[#141418] border border-zinc-700/70 p-3.5 flex flex-col justify-between h-full space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-[9px] font-mono font-bold tracking-widest text-zinc-400 uppercase">
                  DECISION
                </span>
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
              </div>

              <div>
                <div
                  className={`inline-block px-2 py-0.5 rounded text-[11px] font-black tracking-wider uppercase border ${current.decisionColor}`}
                >
                  {current.decision}
                </div>
                <div className="mt-2 text-[10px] text-zinc-400">
                  <span className="font-semibold text-zinc-300">Next Step:</span>{" "}
                  {current.nextStep}
                </div>
              </div>

              <Link
                href={`/ai-analysis?idea=${encodeURIComponent(inputValue)}`}
                className="pt-2 border-t border-zinc-800/80 text-[11px] font-bold text-[#00C29A] hover:text-[#00E5FF] flex items-center justify-between transition-colors group"
              >
                <span>View Full Analysis</span>
                <ArrowRight className="w-3 h-3 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
