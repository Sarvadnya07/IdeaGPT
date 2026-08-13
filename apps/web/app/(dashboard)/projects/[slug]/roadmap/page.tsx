"use client";

import React, { use } from "react";
import Link from "next/link";
import { useProjects } from "@/hooks/useProjects";
import { useRoadmaps } from "@/hooks/useRoadmaps";
import { Map, Plus, CheckCircle2, Circle, Clock, RefreshCw } from "lucide-react";

export default function ProjectRoadmapPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const { projectsQuery } = useProjects();
  const project = projectsQuery.data?.items.find((p) => p.slug === slug);

  const { roadmapsQuery } = useRoadmaps(project?.id || null);
  const roadmaps = roadmapsQuery.data || [];
  const currentRoadmap = roadmaps[0];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-xs mb-1">
            <Map className="w-3.5 h-3.5" />
            <span>Project Roadmap</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">
            {project?.title ? `${project.title} Roadmap` : "Roadmap"}
          </h1>
          <p className="text-neutral-400 text-xs mt-0.5">
            Milestone planning and execution timeline scoped to this project.
          </p>
        </div>
      </div>

      {projectsQuery.isLoading || roadmapsQuery.isLoading ? (
        <div className="flex items-center justify-center py-16 text-neutral-400 gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
          <span className="text-xs">Loading project roadmap...</span>
        </div>
      ) : !currentRoadmap || currentRoadmap.milestones.length === 0 ? (
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-10 text-center max-w-md mx-auto my-8 space-y-3">
          <div className="w-10 h-10 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <Map className="w-5 h-5" />
          </div>
          <h3 className="text-lg font-semibold text-white">No Milestones Planned Yet</h3>
          <p className="text-neutral-400 text-xs">
            Create an execution roadmap to track milestones and technical tasks for this project.
          </p>
          <Link
            href="/roadmap"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Open Roadmap Studio</span>
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {currentRoadmap.milestones.map((m, idx) => (
            <div key={idx} className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-4">
              <div className="flex items-start justify-between gap-4 border-b border-neutral-800 pb-3">
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-wider text-indigo-400 font-semibold">
                    Phase {idx + 1}
                  </div>
                  <h3 className="text-lg font-bold text-white mt-0.5">{m.title}</h3>
                  <p className="text-xs text-neutral-400 mt-1">{m.objective}</p>
                </div>
              </div>

              {/* Tasks List */}
              <div className="space-y-2 pt-1">
                {m.tasks.map((task, tIdx) => (
                  <div
                    key={tIdx}
                    className="flex items-center justify-between p-3 bg-neutral-950/60 border border-neutral-800/80 rounded-lg text-xs"
                  >
                    <div className="flex items-center gap-3">
                      {task.status === "completed" ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                      ) : task.status === "in_progress" ? (
                        <Clock className="w-4 h-4 text-amber-400 shrink-0" />
                      ) : (
                        <Circle className="w-4 h-4 text-neutral-600 shrink-0" />
                      )}
                      <div>
                        <div className="font-medium text-neutral-200">{task.title}</div>
                        {task.description && (
                          <div className="text-[11px] text-neutral-400 mt-0.5">{task.description}</div>
                        )}
                      </div>
                    </div>

                    {task.estimated_days && (
                      <span className="text-[10px] font-mono px-2 py-0.5 bg-neutral-800 text-neutral-400 rounded">
                        {task.estimated_days}d
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
