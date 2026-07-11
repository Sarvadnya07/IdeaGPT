"use client";

import React, { useState } from "react";
import { useIdea } from "../../providers";
import {
  Map,
  Share2,
  Edit2,
  CheckSquare,
  Square,
  AlertOctagon,
  Calendar,
  Layers,
  ChevronRight,
} from "lucide-react";
import { toast } from "sonner";

interface TaskItem {
  id: string;
  name: string;
  done: boolean;
}

interface Phase {
  number: number;
  title: string;
  status: "In Progress" | "Upcoming" | "Completed";
  timeline: string;
  description: string;
  progress: number;
  tasks: TaskItem[];
}

export default function RoadmapPage() {
  const { idea } = useIdea();

  // Dynamic roadmap title
  const roadmapName = idea.title === "Nexus Protocol" ? "Project Genesis" : `${idea.title} Roadmap`;

  // Local state for interactive checkboxes in roadmap
  const [phases, setPhases] = useState<Phase[]>([
    {
      number: 1,
      title: "MVP Development",
      status: "In Progress",
      timeline: "Q3 2024 - Q2 2025",
      description: "Core functionality focusing on data ingestion and basic generative outputs. Validating core assumptions.",
      progress: 65,
      tasks: [
        { id: "1-1", name: "Database Schema & Auth Setup", done: true },
        { id: "1-2", name: "API Integration (OpenAI / Claude)", done: true },
        { id: "1-3", name: "Basic UI/Dashboard Implementation", done: false },
      ],
    },
    {
      number: 2,
      title: "Closed Beta & Refinement",
      status: "Upcoming",
      timeline: "Q3 2025 - Q4 2025",
      description: "Onboarding first 50 early adopters. Refining UX and improving generation latency.",
      progress: 0,
      tasks: [
        { id: "2-1", name: "User Feedback Loop System", done: false },
        { id: "2-2", name: "Latency Optimization (< 2s)", done: false },
      ],
    },
    {
      number: 3,
      title: "Public Launch & Scaling",
      status: "Upcoming",
      timeline: "Q1 2026 - Q2 2026",
      description: "Marketing push, self-serve onboarding, and infrastructure scaling to handle 10k+ concurrent users.",
      progress: 0,
      tasks: [
        { id: "3-1", name: "Automated Billing & Stripe setup", done: false },
        { id: "3-2", name: "Multi-region CDN deployment", done: false },
      ],
    },
  ]);

  const toggleTask = (phaseIndex: number, taskIndex: number) => {
    setPhases((prev) => {
      const copy = [...prev];
      const task = copy[phaseIndex].tasks[taskIndex];
      task.done = !task.done;

      // Recalculate progress for this phase
      const completedCount = copy[phaseIndex].tasks.filter((t) => t.done).length;
      copy[phaseIndex].progress = Math.round(
        (completedCount / copy[phaseIndex].tasks.length) * 100
      );

      if (copy[phaseIndex].progress === 100) {
        copy[phaseIndex].status = "Completed";
      } else if (copy[phaseIndex].progress > 0) {
        copy[phaseIndex].status = "In Progress";
      } else {
        copy[phaseIndex].status = "Upcoming";
      }

      return copy;
    });
    toast.success("Task status updated!");
  };

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Title Segment */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 border-b border-zinc-900 pb-6">
        <div className="space-y-2">
          <span className="text-xs font-bold text-indigo-400 uppercase tracking-widest block">
            Roadmaps
          </span>
          <h1 className="text-4xl font-extrabold tracking-tight text-white">
            {roadmapName}
          </h1>
          <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
            Strategic implementation timeline and milestone tracking for your AI-driven validated idea. Execution prioritized for market entry.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => toast.success("Roadmap exported!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-zinc-300 bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 active:scale-95 rounded-xl transition-all"
          >
            <Share2 className="w-3.5 h-3.5" />
            Export
          </button>
          <button
            onClick={() => toast.success("Phase edit modes opened!")}
            className="flex items-center gap-2 px-4 py-2.5 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-95 rounded-xl transition-all shadow-[0_0_15px_rgba(79,70,229,0.3)]"
          >
            <Edit2 className="w-3.5 h-3.5" />
            Edit Phases
          </button>
        </div>
      </div>

      {/* Primary Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Vertical Timeline Phases */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <div className="flex items-center justify-between border-b border-zinc-900/60 pb-4 mb-6">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Implementation Phases
              </h3>
              <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-wide">
                Q3 2024 - Q2 2026
              </span>
            </div>

            {/* Vertical timeline line */}
            <div className="relative pl-6 border-l border-zinc-800 space-y-8 py-2 ml-3">
              {phases.map((phase, pIdx) => (
                <div key={phase.number} className="relative">
                  {/* Outer Timeline Dot Indicator */}
                  <span className="absolute -left-[31px] top-1 flex items-center justify-center w-[11px] h-[11px] rounded-full bg-zinc-950 border border-zinc-800">
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        phase.status === "Completed"
                          ? "bg-green-500"
                          : phase.status === "In Progress"
                          ? "bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)] animate-pulse"
                          : "bg-zinc-700"
                      }`}
                    ></span>
                  </span>

                  {/* Phase Details Card */}
                  <div className="bg-[#070709] border border-zinc-900/60 rounded-xl p-5 space-y-4 hover:border-zinc-800 transition-all">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest block">
                          Phase {phase.number}
                        </span>
                        <h4 className="text-sm font-bold text-white mt-0.5">
                          {phase.title}
                        </h4>
                      </div>
                      <div className="flex items-center gap-2">
                        {/* Phase Status tag */}
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider border ${
                            phase.status === "Completed"
                              ? "bg-green-500/10 border-green-500/20 text-green-400"
                              : phase.status === "In Progress"
                              ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                              : "bg-zinc-900 border-zinc-800 text-zinc-400"
                          }`}
                        >
                          {phase.status}
                        </span>
                        <span className="text-[10px] font-semibold text-zinc-600 flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {phase.timeline}
                        </span>
                      </div>
                    </div>

                    <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
                      {phase.description}
                    </p>

                    {/* Progress tracking details */}
                    {phase.status !== "Upcoming" && (
                      <div className="space-y-1.5 border-t border-zinc-900/60 pt-3">
                        <div className="flex justify-between text-[9px] font-bold text-zinc-500 uppercase tracking-widest">
                          <span>Progress</span>
                          <span>{phase.progress}%</span>
                        </div>
                        <div className="w-full h-1 bg-zinc-900 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 rounded-full transition-all duration-300"
                            style={{ width: `${phase.progress}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    {/* Task checklist selection */}
                    <div className="space-y-2 border-t border-zinc-900/60 pt-3">
                      {phase.tasks.map((task, tIdx) => (
                        <div
                          key={task.id}
                          onClick={() => toggleTask(pIdx, tIdx)}
                          className="flex items-center gap-2.5 text-xs text-zinc-400 hover:text-zinc-200 cursor-pointer select-none py-1 group"
                        >
                          {task.done ? (
                            <CheckSquare className="w-4 h-4 text-indigo-400 shrink-0" />
                          ) : (
                            <Square className="w-4 h-4 text-zinc-600 group-hover:text-zinc-400 shrink-0" />
                          )}
                          <span className={task.done ? "line-through text-zinc-600 font-medium" : "font-medium"}>
                            {task.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: MVP Scope and Key Risks */}
        <div className="space-y-6">
          {/* MVP Feature Scope Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              MVP Feature Scope
            </h3>

            <div className="space-y-4">
              {/* Feature 1 */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Core Data Ingestion</span>
                  <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold bg-red-500/10 border border-red-500/20 text-red-400">
                    P0
                  </span>
                </div>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  CSV/JSON upload and basic parsing logic.
                </p>
              </div>

              {/* Feature 2 */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Basic Report Gen</span>
                  <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold bg-blue-500/10 border border-blue-500/20 text-blue-400">
                    P1
                  </span>
                </div>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  Standardized PDF export of analysis.
                </p>
              </div>

              {/* Feature 3 */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Dark Mode UI</span>
                  <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-bold bg-zinc-900 border border-zinc-800 text-zinc-400">
                    P2
                  </span>
                </div>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  Theming support for user preferences.
                </p>
              </div>
            </div>
          </div>

          {/* Key Risks Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
              <AlertOctagon className="w-4 h-4 text-orange-400" />
              Key Risks
            </h3>

            <div className="space-y-4">
              {/* Risk 1 */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-orange-400">API Rate Limits</span>
                </div>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  <span className="text-zinc-300 font-semibold">Mitigation:</span> Implement queues and local cache layer in Phase 2.
                </p>
              </div>

              {/* Risk 2 */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-zinc-400">User Retention</span>
                </div>
                <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                  <span className="text-zinc-300 font-semibold">Mitigation:</span> Focus on immediate value delivery in the initial MVP output.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
