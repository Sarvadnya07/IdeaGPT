"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useProjects } from "../../../hooks/useProjects";
import { Folder, Plus, Loader2, Pin, Trash2, Archive, ExternalLink } from "lucide-react";

export default function DashboardPage() {
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [sortBy, setSortBy] = useState("newest");
  const [viewMode, setViewMode] = useState<"grid"|"list">("grid");

  // Debounce search
  React.useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

  const { projectsQuery, createProject, togglePin, toggleArchive, deleteProject, duplicateProject } = useProjects({
    search: debouncedSearch,
    sort_by: sortBy,
    is_archived: false, // We hide archived on main dashboard
  });

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim()) return;
    await createProject.mutateAsync({ title: newTitle, description: newDesc });
    setIsModalOpen(false);
    setNewTitle("");
    setNewDesc("");
  };

  const projects = projectsQuery.data?.items || [];
  const isLoading = projectsQuery.isLoading;

  const pinnedProjects = projects.filter(p => p.is_pinned);
  const standardProjects = projects.filter(p => !p.is_pinned);

  return (
    <div className="space-y-8 py-4 select-none relative">
      <div className="flex justify-between items-center">
        <div className="space-y-2">
          <h1 className="text-3xl font-bold tracking-tight text-white">Your Workspace</h1>
          <p className="text-sm text-zinc-500 max-w-2xl leading-relaxed">
            Manage your AI analysis projects and roadmaps.
          </p>
        </div>
        <Link
          href="/dashboard/projects/new"
          className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Project
        </Link>
      </div>

      <div className="flex gap-4 items-center mb-6">
        <div className="relative max-w-sm w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
          <input 
            type="text" 
            placeholder="Search projects..." 
            className="w-full bg-zinc-900 border border-zinc-800 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-indigo-500"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select 
          value={sortBy} 
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-sm text-white focus:outline-none"
        >
          <option value="newest">Newest First</option>
          <option value="oldest">Oldest First</option>
          <option value="alphabetical">Alphabetical</option>
          <option value="last_opened">Last Opened</option>
        </select>
        <div className="ml-auto flex bg-zinc-900 rounded-lg border border-zinc-800 p-1">
          <button onClick={() => setViewMode("grid")} className={`p-1.5 rounded-md ${viewMode === 'grid' ? 'bg-zinc-800 text-white' : 'text-zinc-500'}`}>Grid</button>
          <button onClick={() => setViewMode("list")} className={`p-1.5 rounded-md ${viewMode === 'list' ? 'bg-zinc-800 text-white' : 'text-zinc-500'}`}>List</button>
        </div>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
        </div>
      ) : projects.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 border border-zinc-800/50 rounded-2xl bg-[#0b0b0d]">
          <Folder className="w-12 h-12 text-zinc-700 mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No projects found</h3>
        </div>
      ) : (
        <div className="space-y-8">
          {pinnedProjects.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest flex items-center gap-2">
                <Pin className="w-4 h-4" /> Pinned
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pinnedProjects.map((p) => (
                  <ProjectCard key={p.id} project={p} togglePin={togglePin} toggleArchive={toggleArchive} deleteProject={deleteProject} duplicateProject={duplicateProject} />
                ))}
              </div>
            </div>
          )}

          {standardProjects.length > 0 && (
            <div className="space-y-4">
              <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">
                All Projects
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {standardProjects.map((p) => (
                  <ProjectCard key={p.id} project={p} togglePin={togglePin} toggleArchive={toggleArchive} deleteProject={deleteProject} duplicateProject={duplicateProject} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ProjectCard({ project, togglePin, toggleArchive, deleteProject, duplicateProject }: any) {
  return (
    <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] hover:border-zinc-700 transition-all group flex flex-col justify-between min-h-[180px]">
      <div className="space-y-3">
        <div className="flex items-start justify-between">
          <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Folder className="w-5 h-5" />
          </div>
          <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button onClick={() => togglePin.mutate(project.id)} className={`p-1.5 rounded-md hover:bg-zinc-800 transition-colors ${project.is_pinned ? 'text-indigo-400' : 'text-zinc-500'}`}>
              <Pin className="w-4 h-4" />
            </button>
            <button onClick={() => duplicateProject.mutate(project.id)} className="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-500 transition-colors">
              <Plus className="w-4 h-4" />
            </button>
            <button onClick={() => toggleArchive.mutate(project.id)} className="p-1.5 rounded-md hover:bg-zinc-800 text-zinc-500 transition-colors">
              <Archive className="w-4 h-4" />
            </button>
            <button onClick={() => deleteProject.mutate(project.id)} className="p-1.5 rounded-md hover:bg-red-500/20 text-zinc-500 hover:text-red-400 transition-colors">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div>
          <h3 className="text-base font-bold text-white line-clamp-1">{project.title}</h3>
          <p className="text-xs text-zinc-500 mt-1 line-clamp-2 leading-relaxed">
            {project.description || "No description provided."}
          </p>
        </div>
      </div>
      <div className="pt-4 mt-4 border-t border-zinc-800/50 flex items-center justify-between">
        <span className="text-[10px] text-zinc-600 font-medium">
          Updated {new Date(project.updated_at).toLocaleDateString()}
        </span>
        <Link href={`/dashboard/projects/${project.slug}`} className="flex items-center gap-1 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors">
          Open <ExternalLink className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
}
