"use client";

import React, { useState } from "react";
import {
  UserCheck,
  Search,
  FileDown,
  FileCheck2,
  Users,
  TrendingUp,
  AlertTriangle,
  Award,
  CheckCircle2,
  Radar,
  Sparkles,
  Calendar,
} from "lucide-react";
import { toast } from "sonner";

export default function RecruiterPage() {
  const [interviewChecklist, setInterviewChecklist] = useState([
    { id: "tech", label: "Technical Validation", desc: "Passed all rigorous technical screens.", done: true },
    { id: "culture", label: "Culture Fit / Values", desc: "Aligned with startup pace and autonomy.", done: true },
    { id: "comp", label: "Compensation Alignment", desc: "Pending final equity discussion.", done: false },
    { id: "ref", label: "References Cleared", desc: "2/3 completed, waiting on former VP.", done: false },
  ]);

  const toggleCheck = (id: string) => {
    setInterviewChecklist((prev) =>
      prev.map((item) => (item.id === id ? { ...item, done: !item.done } : item))
    );
    toast.success("Readiness checklist updated!");
  };

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Top Breadcrumb search header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-500">
            <span>Evaluations</span>
            <span>&gt;</span>
            <span className="text-zinc-400">EM/CTO Simulation</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">
            Candidate Profiling
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search parameters..."
            className="block w-full pl-9 pr-3 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-600"
          />
        </div>
      </div>

      {/* Title Segment and buttons */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <p className="text-xs text-zinc-500 max-w-xl leading-relaxed">
          Real-time analysis of architectural decision-making, code quality, and technical leadership metrics during simulation #EM-882.
        </p>

        {/* Buttons */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toast.success("PDF profile report exported!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 rounded-xl transition-all"
          >
            <FileDown className="w-3.5 h-3.5" />
            Export PDF
          </button>
          <button
            onClick={() => toast.success("Recruiter report finalized successfully!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_15px_rgba(79,70,229,0.3)] rounded-xl transition-all"
          >
            <FileCheck2 className="w-3.5 h-3.5" />
            Finalize Report
          </button>
        </div>
      </div>

      {/* Row 1 Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recruiter Confidence */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] relative overflow-hidden flex flex-col justify-between min-h-[220px]">
          <div className="absolute top-0 right-0 w-[150px] h-[150px] bg-purple-500/5 blur-[50px] pointer-events-none"></div>

          <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3 mb-3">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
              Recruiter Confidence
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[8px] font-bold bg-purple-500/10 border border-purple-500/20 text-purple-400 uppercase tracking-wider">
              ✦ Strong Hire
            </span>
          </div>

          <div className="space-y-2">
            <div className="text-5xl font-black text-white tracking-tight drop-shadow-[0_2px_15px_rgba(255,255,255,0.05)]">
              94%
            </div>
            <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
              Composite score based on technical depth, system design, and communication.
            </p>
          </div>

          <div className="border-t border-zinc-900/60 pt-3 flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
            <span>Percentile Rank</span>
            <span className="text-white">Top 5%</span>
          </div>
        </div>

        {/* Leadership Simulation Metrics */}
        <div className="lg:col-span-2 bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] relative overflow-hidden flex flex-col justify-between min-h-[220px]">
          <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-indigo-500/5 blur-[70px] pointer-events-none"></div>

          <div className="border-b border-zinc-900/60 pb-3 mb-3">
            <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
              Leadership Simulation Metrics
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-2">
            {/* Stat 1 */}
            <div className="space-y-1.5 border-r border-zinc-900/60 last:border-0 pr-4">
              <div className="flex items-center justify-center w-7 h-7 rounded-md bg-indigo-500/10 text-indigo-400">
                <Users className="w-4 h-4" />
              </div>
              <div className="text-2xl font-black text-white mt-1">15+</div>
              <p className="text-[9.5px] text-zinc-500 font-bold uppercase tracking-wider leading-relaxed">
                Cross-Functional Teams Managed
              </p>
            </div>

            {/* Stat 2 */}
            <div className="space-y-1.5 border-r border-zinc-900/60 last:border-0 pr-4">
              <div className="flex items-center justify-center w-7 h-7 rounded-md bg-purple-500/10 text-purple-400">
                <TrendingUp className="w-4 h-4" />
              </div>
              <div className="text-2xl font-black text-white mt-1">3x</div>
              <p className="text-[9.5px] text-zinc-500 font-bold uppercase tracking-wider leading-relaxed">
                Delivery Velocity Increase
              </p>
            </div>

            {/* Stat 3 */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-center w-7 h-7 rounded-md bg-emerald-500/10 text-emerald-400">
                <AlertTriangle className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-black text-white mt-1">0</div>
              <p className="text-[9.5px] text-zinc-500 font-bold uppercase tracking-wider leading-relaxed">
                Protocol Bottlenecks (Simulation)
              </p>
              <span className="text-[8px] font-bold text-emerald-400 block mt-0.5">
                Flawless mitigation
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: Technical Depth Analysis */}
      <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
        <div className="border-b border-zinc-900/60 pb-3 mb-5">
          <h3 className="text-xs font-bold text-white uppercase tracking-wider">
            Technical Depth Analysis
          </h3>
          <p className="text-[10px] text-zinc-500 font-semibold mt-1">
            Evaluated across 5 core competency vectors during live coding and architecture design.
          </p>
        </div>

        <div className="space-y-5">
          {/* Bar 1 */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
              <span>System Architecture & Scalability</span>
              <span className="text-white font-extrabold">98/100</span>
            </div>
            <div className="w-full h-2 bg-zinc-900 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]" style={{ width: "98%" }}></div>
            </div>
          </div>

          {/* Bar 2 */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
              <span>Cloud Native & Infrastructure</span>
              <span className="text-white font-extrabold">92/100</span>
            </div>
            <div className="w-full h-2 bg-zinc-900 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]" style={{ width: "92%" }}></div>
            </div>
          </div>

          {/* Bar 3 */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
              <span>Backend & API Design</span>
              <span className="text-white font-extrabold">88/100</span>
            </div>
            <div className="w-full h-2 bg-zinc-900 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.5)]" style={{ width: "88%" }}></div>
            </div>
          </div>

          {/* Bar 4 */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[9px] font-bold text-zinc-400 uppercase tracking-widest">
              <span>Data Engineering / AI Integration</span>
              <span className="text-pink-400 font-extrabold">95/100</span>
            </div>
            <div className="w-full h-2 bg-zinc-900 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full shadow-[0_0_8px_rgba(236,72,153,0.5)]" style={{ width: "95%" }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3 Triple Columns */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Column 1: Architect Maturity */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[280px]">
          <div className="border-b border-zinc-900/60 pb-3 mb-3">
            <h3 className="text-[10px] font-bold text-white uppercase tracking-widest">
              Architects Maturity
            </h3>
          </div>

          {/* Visual node layout */}
          <div className="flex-1 flex flex-col justify-center items-center py-4 relative">
            <div className="w-20 h-20 rounded-full border border-zinc-800/80 flex items-center justify-center relative">
              <div className="absolute w-2 h-2 rounded-full bg-indigo-500 -top-1 left-2"></div>
              <div className="absolute w-2 h-2 rounded-full bg-purple-500 bottom-2 -right-1"></div>
              <div className="absolute w-2 h-2 rounded-full bg-pink-500 bottom-1 left-2"></div>
              <Radar className="w-7 h-7 text-indigo-400" />
            </div>
          </div>

          <div className="space-y-1 text-[10px] font-semibold text-zinc-500 border-t border-zinc-900/60 pt-3">
            <div className="flex justify-between">
              <span>• Microservices</span>
              <span className="text-zinc-300">Advanced</span>
            </div>
            <div className="flex justify-between">
              <span>• Event-Driven</span>
              <span className="text-zinc-300">Expert</span>
            </div>
            <div className="flex justify-between">
              <span>• Security by Design</span>
              <span className="text-zinc-300">Proficient</span>
            </div>
          </div>
        </div>

        {/* Column 2: Quality Review Feedback */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] min-h-[280px]">
          <div className="border-b border-zinc-900/60 pb-3 mb-4">
            <h3 className="text-[10px] font-bold text-white uppercase tracking-widest">
              Quality Review Feedback
            </h3>
          </div>

          <div className="space-y-4">
            {/* Box 1 */}
            <div className="bg-[#070709] border border-zinc-900/60 rounded-xl p-3.5 space-y-1">
              <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-widest block">
                [x] Clean Abstractions
              </span>
              <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                Demonstrated excellent use of interface segregation during the payment gateway design exercise. Highly maintainable.
              </p>
            </div>

            {/* Box 2 */}
            <div className="bg-[#070709] border border-zinc-900/60 rounded-xl p-3.5 space-y-1">
              <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-widest block">
                [x] Edge Case Handling
              </span>
              <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                Proactively identified and mitigated simulated transaction failures without prompt.
              </p>
            </div>
          </div>
        </div>

        {/* Column 3: CTO Interview Readiness */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[280px]">
          <div>
            <div className="border-b border-zinc-900/60 pb-3 mb-4">
              <h3 className="text-[10px] font-bold text-white uppercase tracking-widest">
                SaaS Interview Readiness
              </h3>
            </div>

            <div className="space-y-3">
              {interviewChecklist.map((item) => (
                <div
                  key={item.id}
                  onClick={() => toggleCheck(item.id)}
                  className="flex items-start gap-2.5 cursor-pointer py-0.5 group"
                >
                  <div className={`w-3.5 h-3.5 border rounded mt-0.5 flex items-center justify-center shrink-0 transition-all ${
                    item.done ? "bg-indigo-600 border-indigo-500 text-white" : "border-zinc-800 group-hover:border-zinc-600 text-transparent"
                  }`}>
                    <CheckCircle2 className="w-3 h-3 text-white" />
                  </div>
                  <div className="space-y-0.5">
                    <span className={`text-[10.5px] font-bold text-white block ${item.done && "text-zinc-650"}`}>
                      {item.label}
                    </span>
                    <span className="text-[9px] text-zinc-500 leading-relaxed font-medium block">
                      {item.desc}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={() => toast.success("CTO interview round scheduled!")}
            className="w-full mt-4 py-2.5 text-[9px] font-bold text-white bg-[#0c0c0e] border border-zinc-850 hover:bg-zinc-800 hover:border-zinc-700 active:scale-[0.98] rounded-xl transition-all uppercase tracking-widest flex items-center justify-center gap-2"
          >
            <Calendar className="w-3.5 h-3.5 text-zinc-500" />
            Schedule CTO Round
          </button>
        </div>
      </div>
    </div>
  );
}
