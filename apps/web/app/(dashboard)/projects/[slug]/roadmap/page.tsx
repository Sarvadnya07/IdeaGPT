"use client";

import React, { use, useState } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useIdea } from "@/hooks/useIdea";
import { useRoadmaps, Milestone } from "@/hooks/useRoadmaps";
import { useApiClient } from "@/lib/api/client";
import { Map, Plus, CheckCircle2, Circle, Clock, RefreshCw, Sparkles, BrainCircuit, Loader2 } from "lucide-react";
import { toast } from "sonner";

export default function ProjectRoadmapPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const api = useApiClient();
  const { projectsQuery } = useProjects();
  const project = projectsQuery.data?.items.find((p) => p.slug === slug);

  const { roadmapsQuery, createRoadmap, updateRoadmap } = useRoadmaps(project?.id || null);
  const roadmaps = roadmapsQuery.data || [];
  const currentRoadmap = roadmaps[0];

  const { ideasQuery } = useIdea(project?.id);
  const projectIdeas = ideasQuery.data || [];
  const primaryIdea = projectIdeas[0];

  const [selectedModel, setSelectedModel] = useState<string>("openai/gpt-oss-120b");
  const [isGeneratingAI, setIsGeneratingAI] = useState<boolean>(false);

  const handleGenerateAIRoadmap = async () => {
    if (!project?.id) return;
    setIsGeneratingAI(true);
    try {
      const res = await api.post<any>("/ai/roadmap", {
        title: primaryIdea?.title || project?.title || "Startup Product",
        category: primaryIdea?.industry || project?.category || "B2B SaaS",
        problem_statement: primaryIdea?.problem_statement || "",
        solution_description: primaryIdea?.solution_description || "",
        target_users: primaryIdea?.target_users || "",
        provider: "groq",
        model: selectedModel,
      });

      const generatedMilestones: Milestone[] = res.data.milestones;

      if (currentRoadmap) {
        await updateRoadmap.mutateAsync({
          roadmapId: currentRoadmap.id,
          data: { milestones: generatedMilestones },
        });
      } else {
        await createRoadmap.mutateAsync({
          milestones: generatedMilestones,
          status: "active",
        });
      }
      toast.success(`Dynamic AI roadmap generated with ${selectedModel}!`);
    } catch (err) {
      toast.error("Failed to generate AI roadmap.");
    } finally {
      setIsGeneratingAI(false);
    }
  };

  const handleToggleTaskStatus = async (milestoneIdx: number, taskIdx: number) => {
    if (!currentRoadmap) return;

    const updatedMilestones = JSON.parse(JSON.stringify(currentRoadmap.milestones)) as Milestone[];
    const currentStatus = updatedMilestones[milestoneIdx].tasks[taskIdx].status;

    const nextStatus =
      currentStatus === "pending"
        ? "in_progress"
        : currentStatus === "in_progress"
        ? "completed"
        : "pending";

    updatedMilestones[milestoneIdx].tasks[taskIdx].status = nextStatus;

    try {
      await updateRoadmap.mutateAsync({
        roadmapId: currentRoadmap.id,
        data: { milestones: updatedMilestones },
      });
      const statusLabel = nextStatus === "completed" ? "Completed" : nextStatus === "in_progress" ? "In Progress" : "Pending";
      toast.success(`Task marked as ${statusLabel}`);
    } catch (err) {
      toast.error("Failed to update task status.");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-xs mb-1">
            <Map className="w-3.5 h-3.5" />
            <span>Project Roadmap</span>
            <span className="bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 text-[10px] px-2 py-0.5 rounded font-mono">⚡ Powered by Groq</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            {project?.title ? `${project.title} Roadmap` : "Roadmap"}
          </h1>
          <p className="text-neutral-400 text-xs mt-0.5">
            Interactive milestone planning and task execution tracker. Click any task to toggle status.
          </p>
        </div>

        {currentRoadmap && currentRoadmap.milestones.length > 0 && (
          <div className="flex items-center gap-2">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-neutral-900 border border-neutral-800 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="openai/gpt-oss-120b">GPT-OSS 120B (Groq)</option>
              <option value="qwen/qwen3.8-27b">Qwen 3.8 27B (Groq)</option>
              <option value="openai/gpt-oss-20b">GPT-OSS 20B (Groq)</option>
            </select>

            <button
              onClick={handleGenerateAIRoadmap}
              disabled={isGeneratingAI}
              className="flex items-center gap-1.5 px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-all disabled:opacity-50 shadow-[0_0_15px_rgba(79,70,229,0.3)]"
            >
              {isGeneratingAI ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
              Regenerate with Groq
            </button>
          </div>
        )}
      </div>

      {projectsQuery.isLoading || roadmapsQuery.isLoading ? (
        <div className="flex items-center justify-center py-16 text-neutral-400 gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
          <span className="text-xs">Loading project roadmap...</span>
        </div>
      ) : !currentRoadmap || currentRoadmap.milestones.length === 0 ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-10 text-center max-w-md mx-auto my-8 space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center mx-auto text-indigo-400">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-semibold text-white">No Milestones Planned Yet</h3>
          <p className="text-neutral-400 text-xs leading-relaxed">
            Generate an AI-synthesized execution roadmap with customized phases, objectives, and task trackers.
          </p>

          <div className="flex flex-col items-center gap-3 pt-2">
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-black/80 border border-neutral-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              <option value="openai/gpt-oss-120b">GPT-OSS 120B (Groq)</option>
              <option value="qwen/qwen3.8-27b">Qwen 3.8 27B (Groq)</option>
              <option value="openai/gpt-oss-20b">GPT-OSS 20B (Groq)</option>
            </select>

            <button
              onClick={handleGenerateAIRoadmap}
              disabled={isGeneratingAI}
              className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold px-6 py-2.5 rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] disabled:opacity-50"
            >
              {isGeneratingAI ? <Loader2 className="w-4 h-4 animate-spin" /> : <BrainCircuit className="w-4 h-4" />}
              <span>Generate AI Roadmap</span>
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {currentRoadmap.milestones.map((m, idx) => {
            const completedCount = m.tasks.filter(t => t.status === "completed").length;
            const progressPercent = m.tasks.length > 0 ? Math.round((completedCount / m.tasks.length) * 100) : 0;

            return (
              <div key={idx} className="bg-neutral-900/90 border border-neutral-800 rounded-xl p-5 space-y-4">
                <div className="flex items-start justify-between gap-4 border-b border-neutral-800/80 pb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-indigo-400 font-semibold">
                        Phase {idx + 1}
                      </span>
                      <span className="text-[10px] bg-neutral-800 text-neutral-400 px-2 py-0.5 rounded font-mono">
                        {completedCount}/{m.tasks.length} Completed ({progressPercent}%)
                      </span>
                    </div>
                    <h3 className="text-lg font-bold text-white mt-1">{m.title}</h3>
                    <p className="text-xs text-neutral-400 mt-1">{m.objective}</p>
                  </div>

                  <button
                    onClick={handleGenerateAIRoadmap}
                    disabled={isGeneratingAI}
                    className="text-[11px] flex items-center gap-1 text-zinc-400 hover:text-indigo-400 px-2.5 py-1 rounded bg-neutral-800/60 hover:bg-neutral-800 transition-colors"
                  >
                    <RefreshCw className="w-3 h-3" /> Regenerate
                  </button>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-neutral-950 h-1.5 rounded-full overflow-hidden border border-neutral-800">
                  <div 
                    className="bg-indigo-500 h-full transition-all duration-300 rounded-full" 
                    style={{ width: `${progressPercent}%` }} 
                  />
                </div>

                {/* Tasks List */}
                <div className="space-y-2 pt-1">
                  {m.tasks.map((task, tIdx) => (
                    <button
                      key={tIdx}
                      type="button"
                      onClick={() => handleToggleTaskStatus(idx, tIdx)}
                      className="w-full text-left flex items-center justify-between p-3 bg-neutral-950/60 hover:bg-neutral-950 border border-neutral-800/80 hover:border-neutral-700 rounded-lg text-xs transition-all group cursor-pointer"
                    >
                      <div className="flex items-center gap-3">
                        {task.status === "completed" ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        ) : task.status === "in_progress" ? (
                          <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                        ) : (
                          <Circle className="w-4 h-4 text-neutral-600 group-hover:text-neutral-400 shrink-0" />
                        )}
                        <div>
                          <div className={`font-medium transition-colors ${task.status === "completed" ? "text-neutral-400 line-through" : "text-neutral-200"}`}>
                            {task.title}
                          </div>
                          {task.description && (
                            <div className="text-[11px] text-neutral-500 mt-0.5">{task.description}</div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0">
                        <span className={`text-[10px] font-semibold px-2 py-0.5 rounded capitalize ${
                          task.status === "completed" 
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : task.status === "in_progress"
                            ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            : "bg-neutral-800 text-neutral-400"
                        }`}>
                          {task.status.replace("_", " ")}
                        </span>

                        {task.estimated_days && (
                          <span className="text-[10px] font-mono px-2 py-0.5 bg-neutral-850 text-neutral-400 rounded">
                            {task.estimated_days}d
                          </span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
