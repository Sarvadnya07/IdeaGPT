"use client";

import React, { useState } from "react";
import { useProjects } from "../../../hooks/useProjects";
import { useRoadmaps, Milestone, Task, Roadmap } from "../../../hooks/useRoadmaps";
import {
  Map,
  Plus,
  Loader2,
  Trash2,
  CheckCircle2,
  Circle,
  Clock,
  ChevronRight,
  Sparkles,
  Layers,
} from "lucide-react";
import { toast } from "sonner";

export default function RoadmapPage() {
  const { projectsQuery } = useProjects();
  const projects = projectsQuery.data?.items || [];
  
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");

  // Default to first project if available and none selected
  const activeProjectId = selectedProjectId || (projects.length > 0 ? projects[0].id : null);
  const activeProject = projects.find((p) => p.id === activeProjectId);

  const { roadmapsQuery, createRoadmap, updateRoadmap, deleteRoadmap } = useRoadmaps(activeProjectId);
  const roadmaps = roadmapsQuery.data || [];
  const activeRoadmap = roadmaps.length > 0 ? roadmaps[0] : null;

  // New Milestone Form State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [milestoneTitle, setMilestoneTitle] = useState("");
  const [milestoneObjective, setMilestoneObjective] = useState("");
  const [taskTitle, setTaskTitle] = useState("");
  const [taskDays, setTaskDays] = useState<number>(3);

  const handleCreateRoadmap = async () => {
    if (!activeProjectId) return;
    try {
      const initialMilestones: Milestone[] = [
        {
          title: "Phase 1: Foundation & Architecture",
          objective: "Establish core project infrastructure and database models",
          tasks: [
            { title: "Define Database Schemas & Migrations", estimated_days: 2, status: "completed" },
            { title: "Setup Authentication & User Sync", estimated_days: 3, status: "completed" },
            { title: "Configure API Routes & Middleware", estimated_days: 2, status: "in_progress" },
          ],
        },
        {
          title: "Phase 2: MVP Execution",
          objective: "Deliver key evaluation feature set and analytics",
          tasks: [
            { title: "Integrate AI Provider Pipeline", estimated_days: 5, status: "pending" },
            { title: "Build Interactive Analysis Dashboard", estimated_days: 4, status: "pending" },
          ],
        },
      ];

      await createRoadmap.mutateAsync({
        milestones: initialMilestones,
        status: "active",
      });
      toast.success("Product roadmap initialized!");
    } catch (err) {
      toast.error("Failed to create roadmap.");
    }
  };

  const handleAddMilestone = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeRoadmap || !milestoneTitle.trim()) return;

    const newMilestone: Milestone = {
      title: milestoneTitle,
      objective: milestoneObjective || "Milestone objective",
      tasks: taskTitle.trim()
        ? [{ title: taskTitle, estimated_days: taskDays, status: "pending" }]
        : [],
    };

    const updatedMilestones = [...activeRoadmap.milestones, newMilestone];

    try {
      await updateRoadmap.mutateAsync({
        roadmapId: activeRoadmap.id,
        data: { milestones: updatedMilestones },
      });
      toast.success("Milestone added to roadmap!");
      setIsModalOpen(false);
      setMilestoneTitle("");
      setMilestoneObjective("");
      setTaskTitle("");
    } catch (err) {
      toast.error("Failed to update roadmap.");
    }
  };

  const handleToggleTaskStatus = async (milestoneIdx: number, taskIdx: number) => {
    if (!activeRoadmap) return;

    const updatedMilestones = JSON.parse(JSON.stringify(activeRoadmap.milestones)) as Milestone[];
    const currentStatus = updatedMilestones[milestoneIdx].tasks[taskIdx].status;

    const nextStatus: Task["status"] =
      currentStatus === "pending"
        ? "in_progress"
        : currentStatus === "in_progress"
        ? "completed"
        : "pending";

    updatedMilestones[milestoneIdx].tasks[taskIdx].status = nextStatus;

    try {
      await updateRoadmap.mutateAsync({
        roadmapId: activeRoadmap.id,
        data: { milestones: updatedMilestones },
      });
    } catch (err) {
      toast.error("Failed to update task status.");
    }
  };

  const handleDeleteRoadmap = async () => {
    if (!activeRoadmap) return;
    if (confirm("Are you sure you want to delete this roadmap?")) {
      try {
        await deleteRoadmap.mutateAsync(activeRoadmap.id);
        toast.success("Roadmap deleted.");
      } catch (err) {
        toast.error("Failed to delete roadmap.");
      }
    }
  };

  return (
    <div className="space-y-8 py-4 select-none max-w-6xl mx-auto">
      {/* Top Heading & Project Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-6">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <Map className="w-4 h-4" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-white">Product Roadmaps</h1>
          </div>
          <p className="text-xs text-zinc-500 max-w-2xl leading-relaxed">
            Track execution timelines, milestones, and task statuses across your projects.
          </p>
        </div>

        {/* Project Dropdown */}
        {projects.length > 0 && (
          <div className="flex items-center gap-3">
            <label className="text-xs font-bold text-zinc-400 uppercase tracking-wider">Project:</label>
            <select
              value={activeProjectId || ""}
              onChange={(e) => setSelectedProjectId(e.target.value)}
              className="bg-[#0b0b0d] border border-zinc-800 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {/* Loading State */}
      {projectsQuery.isLoading || roadmapsQuery.isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
      ) : projects.length === 0 ? (
        /* Empty State: No Projects */
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <Layers className="w-12 h-12 text-zinc-700 mb-2" />
          <h3 className="text-lg font-bold text-white">No Projects Available</h3>
          <p className="text-xs text-zinc-500 max-w-md">
            Create your first project from the dashboard before generating a product roadmap.
          </p>
        </div>
      ) : !activeRoadmap ? (
        /* Empty State: Project Has No Roadmap */
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-900/60 rounded-2xl bg-[#0b0b0d] text-center p-8 space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-2">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-white">No Roadmap for {activeProject?.title}</h3>
          <p className="text-xs text-zinc-500 max-w-md leading-relaxed">
            Initialize an active execution roadmap with key phases, objectives, and task trackers.
          </p>
          <button
            onClick={handleCreateRoadmap}
            disabled={createRoadmap.isPending}
            className="flex items-center gap-2 px-6 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)] mt-2"
          >
            {createRoadmap.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Plus className="w-4 h-4" />
            )}
            Initialize Roadmap
          </button>
        </div>
      ) : (
        /* Populated State: Active Roadmap View */
        <div className="space-y-6">
          {/* Action Header */}
          <div className="flex items-center justify-between bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-4 px-6">
            <div className="flex items-center gap-3">
              <span className="text-xs font-bold text-zinc-400 uppercase tracking-widest">Status:</span>
              <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                {activeRoadmap.status}
              </span>
              <span className="text-xs text-zinc-600">
                • {activeRoadmap.milestones.length} Milestones
              </span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setIsModalOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold transition-all"
              >
                <Plus className="w-3.5 h-3.5" /> Add Milestone
              </button>
              <button
                onClick={handleDeleteRoadmap}
                className="p-1.5 rounded-lg hover:bg-red-500/10 text-zinc-500 hover:text-red-400 border border-transparent hover:border-red-500/20 transition-all"
                title="Delete Roadmap"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Timeline Milestones */}
          <div className="space-y-6">
            {activeRoadmap.milestones.map((milestone, mIdx) => (
              <div
                key={mIdx}
                className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)] space-y-4"
              >
                <div className="flex items-start justify-between border-b border-zinc-900/60 pb-3">
                  <div>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      <span className="w-6 h-6 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center text-xs font-black">
                        {mIdx + 1}
                      </span>
                      {milestone.title}
                    </h3>
                    <p className="text-xs text-zinc-500 mt-1 font-medium leading-relaxed">
                      {milestone.objective}
                    </p>
                  </div>
                </div>

                {/* Tasks List */}
                <div className="space-y-2 pt-2">
                  {milestone.tasks.length === 0 ? (
                    <div className="text-xs text-zinc-600 italic">No tasks listed for this milestone.</div>
                  ) : (
                    milestone.tasks.map((task, tIdx) => (
                      <div
                        key={tIdx}
                        onClick={() => handleToggleTaskStatus(mIdx, tIdx)}
                        className="flex items-center justify-between p-3 bg-[#070709] border border-zinc-900 rounded-xl hover:border-zinc-800 transition-all cursor-pointer group"
                      >
                        <div className="flex items-center gap-3">
                          {task.status === "completed" ? (
                            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                          ) : task.status === "in_progress" ? (
                            <Clock className="w-4 h-4 text-indigo-400 shrink-0 animate-pulse" />
                          ) : (
                            <Circle className="w-4 h-4 text-zinc-600 shrink-0 group-hover:text-zinc-400" />
                          )}
                          <span
                            className={`text-xs font-semibold ${
                              task.status === "completed"
                                ? "text-zinc-500 line-through"
                                : "text-zinc-200"
                            }`}
                          >
                            {task.title}
                          </span>
                        </div>

                        <div className="flex items-center gap-3">
                          {task.estimated_days && (
                            <span className="text-[10px] text-zinc-600 font-medium">
                              {task.estimated_days}d est.
                            </span>
                          )}
                          <span
                            className={`text-[9px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border ${
                              task.status === "completed"
                                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                                : task.status === "in_progress"
                                ? "bg-indigo-500/10 text-indigo-400 border-indigo-500/20"
                                : "bg-zinc-900 text-zinc-500 border-zinc-800"
                            }`}
                          >
                            {task.status.replace("_", " ")}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Add Milestone Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-[#0b0b0d] border border-zinc-800 rounded-2xl p-6 max-w-md w-full space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Add Milestone</h3>
            <form onSubmit={handleAddMilestone} className="space-y-4">
              <div>
                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest block mb-1">
                  Milestone Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Phase 3: Scaling & Analytics"
                  value={milestoneTitle}
                  onChange={(e) => setMilestoneTitle(e.target.value)}
                  className="w-full bg-[#070709] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest block mb-1">
                  Objective
                </label>
                <input
                  type="text"
                  placeholder="e.g. Implement multi-region caching and load testing"
                  value={milestoneObjective}
                  onChange={(e) => setMilestoneObjective(e.target.value)}
                  className="w-full bg-[#070709] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest block mb-1">
                  Initial Task
                </label>
                <input
                  type="text"
                  placeholder="e.g. Setup Redis cluster"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  className="w-full bg-[#070709] border border-zinc-800 rounded-xl px-4 py-2.5 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-zinc-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={updateRoadmap.isPending}
                  className="px-4 py-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 rounded-xl transition-all"
                >
                  {updateRoadmap.isPending ? <Loader2 className="w-4 h-4 animate-spin" /> : "Save Milestone"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
