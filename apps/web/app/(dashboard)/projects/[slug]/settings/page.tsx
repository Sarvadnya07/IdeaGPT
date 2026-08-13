"use client";

import React, { use, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useProjectBySlug, useUpdateProject, useDeleteProject } from "@/hooks/useProjects";
import { Settings, Save, Trash2, AlertTriangle, RefreshCw, CheckCircle2 } from "lucide-react";

export default function ProjectSettingsPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = use(params);
  const router = useRouter();

  const { projectQuery } = useProjectBySlug(slug);
  const project = projectQuery.data;

  const updateProject = useUpdateProject();
  const deleteProject = useDeleteProject();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("draft");
  const [visibility, setVisibility] = useState("private");

  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    if (project) {
      setTitle(project.title || "");
      setDescription(project.description || "");
      setCategory(project.category || "");
      setStatus(project.status || "draft");
      setVisibility(project.visibility || "private");
    }
  }, [project]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!project?.id) return;

    setErrorMsg(null);
    setSaveSuccess(false);

    try {
      await updateProject.mutateAsync({
        id: project.id,
        data: {
          title,
          description,
          category,
          status,
          visibility,
        },
      });
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: any) {
      console.error("Failed to update project settings:", err);
      setErrorMsg("Failed to save project settings. Please try again.");
    }
  };

  const handleSoftDelete = async () => {
    if (!project?.id) return;
    const confirmDelete = window.confirm(
      `Are you sure you want to archive "${project.title}"? This project will be soft-deleted.`
    );
    if (!confirmDelete) return;

    try {
      await deleteProject.mutateAsync(project.id);
      router.push("/dashboard");
    } catch (err: any) {
      console.error("Failed to delete project:", err);
      setErrorMsg("Failed to archive project.");
    }
  };

  return (
    <div className="space-y-6 max-w-3xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-neutral-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-xs mb-1">
            <Settings className="w-3.5 h-3.5" />
            <span>Project Configuration</span>
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Project Settings</h1>
          <p className="text-neutral-400 text-xs mt-0.5">
            Manage metadata, status, visibility, and archiving options for this project.
          </p>
        </div>
      </div>

      {projectQuery.isLoading ? (
        <div className="flex items-center justify-center py-16 text-neutral-400 gap-2">
          <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
          <span className="text-xs">Loading project settings...</span>
        </div>
      ) : !project ? (
        <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-8 text-center text-red-300 text-xs">
          Project not found.
        </div>
      ) : (
        <div className="space-y-8">
          {/* Settings Form */}
          <form onSubmit={handleSave} className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-5">
            {saveSuccess && (
              <div className="bg-emerald-950/50 border border-emerald-800/60 rounded-lg p-3 flex items-center gap-2 text-emerald-300 text-xs">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>Project settings updated successfully!</span>
              </div>
            )}

            {errorMsg && (
              <div className="bg-red-950/50 border border-red-800/60 rounded-lg p-3 flex items-center gap-2 text-red-300 text-xs">
                <AlertTriangle className="w-4 h-4 text-red-400" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Title */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-neutral-300">Project Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                required
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-3.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Description */}
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-neutral-300">Description</label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-3.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Category & Status */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-neutral-300">Category</label>
                <input
                  type="text"
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  placeholder="e.g. Developer Tools, SaaS, AI"
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-3.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-neutral-300">Status</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-full bg-neutral-950 border border-neutral-800 rounded-lg px-3.5 py-2 text-xs text-white focus:outline-none focus:border-indigo-500 cursor-pointer"
                >
                  <option value="draft">Draft</option>
                  <option value="active">Active</option>
                  <option value="archived">Archived</option>
                </select>
              </div>
            </div>

            {/* Save Action */}
            <div className="flex justify-end pt-2">
              <button
                type="submit"
                disabled={updateProject.isPending}
                className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer shadow-lg shadow-indigo-950/50"
              >
                {updateProject.isPending ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5" />
                    <span>Save Settings</span>
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Danger Zone: Soft Delete */}
          <div className="bg-red-950/20 border border-red-900/40 rounded-xl p-6 space-y-3">
            <h3 className="text-sm font-bold text-red-400 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              <span>Archive / Delete Project</span>
            </h3>
            <p className="text-xs text-neutral-400">
              Soft-deletes this project by setting <span className="font-mono text-neutral-300">deleted_at</span>. The project can be recovered if needed.
            </p>
            <div className="pt-2">
              <button
                onClick={handleSoftDelete}
                disabled={deleteProject.isPending}
                className="inline-flex items-center gap-2 bg-red-900/60 hover:bg-red-800/80 border border-red-700/60 text-red-200 text-xs font-medium px-4 py-2 rounded-lg transition-colors cursor-pointer"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Archive Project</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
