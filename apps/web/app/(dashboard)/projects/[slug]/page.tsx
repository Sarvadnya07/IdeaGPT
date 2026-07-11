"use client";

import React from "react";
import { useProjects } from "../../../../hooks/useProjects";
import { AlertTriangle, Clock, Trash2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function ProjectOverviewPage({ params }: { params: { slug: string } }) {
  const router = useRouter();
  const { projectsQuery, deleteProject } = useProjects();
  
  const project = projectsQuery.data?.items.find(p => p.slug === params.slug);

  if (projectsQuery.isLoading) return <div className="py-20 text-center text-zinc-500 animate-pulse">Loading Workspace...</div>;
  if (!project) return <div className="py-20 text-center text-red-400">Project Not Found.</div>;

  const handleDelete = async () => {
    if (confirm("Are you sure you want to permanently delete this project?")) {
      await deleteProject.mutateAsync(project.id);
      router.push("/dashboard");
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">{project.title}</h1>
          <p className="text-zinc-400 max-w-3xl leading-relaxed">{project.description || "No description provided."}</p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <span className="px-2 py-1 bg-zinc-800 rounded text-xs text-zinc-400 border border-zinc-700">
            {project.category || "Uncategorized"}
          </span>
          <span className="text-xs text-zinc-600 flex items-center gap-1 mt-2">
            <Clock className="w-3 h-3" /> Updated {new Date(project.updated_at).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Quick Stats / Actions */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-[#0b0b0d] border border-zinc-800/60 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Pending Actions</h3>
            <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-4 text-sm text-indigo-200">
              Complete your startup profile to generate an AI evaluation.
            </div>
          </div>
          
          <div className="bg-[#0b0b0d] border border-zinc-800/60 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4">Recent Activity</h3>
            <p className="text-zinc-500 text-sm">Workspace initialized.</p>
          </div>
        </div>

        {/* Sidebar / Danger Zone */}
        <div className="space-y-6">
          <div className="bg-[#0b0b0d] border border-red-900/20 rounded-xl p-6">
            <h3 className="text-sm font-bold text-red-500 flex items-center gap-2 mb-4 uppercase tracking-wider">
              <AlertTriangle className="w-4 h-4" /> Danger Zone
            </h3>
            <p className="text-xs text-zinc-500 mb-4 leading-relaxed">
              Permanently delete this project and all associated AI analysis, reports, and roadmaps. This action cannot be undone.
            </p>
            <button
              onClick={handleDelete}
              className="w-full flex items-center justify-center gap-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/20 px-4 py-2 rounded-lg text-sm font-bold transition-colors"
            >
              <Trash2 className="w-4 h-4" /> Delete Project
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
