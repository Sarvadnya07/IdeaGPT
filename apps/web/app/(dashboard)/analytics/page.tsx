"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useAnalytics } from "@/hooks/useAnalytics";
import { useProjects } from "@/hooks/useProjects";
import {
  BarChart3,
  TrendingUp,
  Layers,
  Lightbulb,
  CheckCircle2,
  AlertTriangle,
  Award,
  RefreshCw,
  Plus,
  Calendar,
  Filter,
  Activity,
  FileText,
} from "lucide-react";

export default function AnalyticsPage() {
  const [range, setRange] = useState<string>("all");
  const [selectedProjectId, setSelectedProjectId] = useState<string>("");

  const { projectsQuery } = useProjects({ limit: 50 });
  const projects = projectsQuery.data?.items || [];

  const { analyticsQuery } = useAnalytics(
    range,
    selectedProjectId || undefined,
  );
  const data = analyticsQuery.data;

  const timeRangeTabs = [
    { id: "7d", label: "7 Days" },
    { id: "30d", label: "30 Days" },
    { id: "90d", label: "90 Days" },
    { id: "1y", label: "1 Year" },
    { id: "all", label: "All Time" },
  ];

  return (
    <div className="min-h-screen bg-neutral-950 text-neutral-100 p-6 md:p-10 space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-b border-neutral-800 pb-6">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-medium text-sm mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>Platform Intelligence & Performance</span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Analytics & Insights
          </h1>
          <p className="text-neutral-400 text-sm mt-1">
            Deterministic evaluation metrics, project velocity, score
            distributions, and creation trends.
          </p>
        </div>

        {/* Filters Bar */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Time Range Tabs */}
          <div className="flex items-center bg-neutral-900 border border-neutral-800 rounded-lg p-1">
            {timeRangeTabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setRange(tab.id)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                  range === tab.id
                    ? "bg-indigo-600 text-white shadow-sm"
                    : "text-neutral-400 hover:text-neutral-200"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Project Filter */}
          {projects.length > 0 && (
            <div className="flex items-center gap-2 bg-neutral-900 border border-neutral-800 rounded-lg p-2">
              <Filter className="w-3.5 h-3.5 text-neutral-400 ml-1" />
              <select
                value={selectedProjectId}
                onChange={(e) => setSelectedProjectId(e.target.value)}
                className="bg-transparent text-xs text-neutral-200 focus:outline-none cursor-pointer pr-2"
              >
                <option value="" className="bg-neutral-900 text-neutral-200">
                  All Projects
                </option>
                {projects.map((p) => (
                  <option
                    key={p.id}
                    value={p.id}
                    className="bg-neutral-900 text-neutral-200"
                  >
                    {p.title}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Main Content View */}
      {analyticsQuery.isLoading ? (
        <div className="flex items-center justify-center py-24 text-neutral-400 gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-indigo-400" />
          <span>Aggregating workspace analytics...</span>
        </div>
      ) : analyticsQuery.isError ? (
        <div className="bg-red-950/40 border border-red-800/60 rounded-xl p-8 text-center max-w-lg mx-auto my-12 space-y-3 text-red-300">
          <AlertTriangle className="w-8 h-8 text-red-400 mx-auto" />
          <h3 className="text-lg font-semibold text-white">
            Failed to Load Analytics
          </h3>
          <p className="text-xs text-neutral-400">
            An error occurred while deriving metric statistics from the backend
            server.
          </p>
          <button
            onClick={() => analyticsQuery.refetch()}
            className="px-4 py-2 bg-neutral-800 hover:bg-neutral-700 text-neutral-200 rounded-lg text-xs font-medium transition-colors"
          >
            Retry Query
          </button>
        </div>
      ) : !data || data.summary.total_projects === 0 ? (
        /* Empty State: 0 Projects / Data */
        <div className="bg-neutral-900/50 border border-neutral-800 rounded-xl p-12 text-center max-w-lg mx-auto my-12 space-y-4">
          <div className="w-12 h-12 rounded-full bg-neutral-800 flex items-center justify-center mx-auto text-neutral-400">
            <Activity className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-semibold text-white">
            No Analytics Data Yet
          </h3>
          <p className="text-neutral-400 text-sm">
            Create your first project and run an evaluation to start tracking
            metrics and trends.
          </p>
          <Link
            href="/projects/new"
            className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors shadow-lg shadow-indigo-950/50"
          >
            <Plus className="w-4 h-4" />
            <span>Create First Project</span>
          </Link>
        </div>
      ) : (
        /* Populated Analytics Dashboard */
        <div className="space-y-8">
          {/* Top KPI Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            {/* Card 1: Total Projects */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-2">
              <div className="flex items-center justify-between text-neutral-400">
                <span className="text-xs font-medium">Total Projects</span>
                <Layers className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-3xl font-bold text-white">
                {data.summary.total_projects}
              </div>
              <div className="text-xs text-neutral-400 flex items-center justify-between pt-1">
                <span>Active Workspace</span>
                <span className="text-neutral-300 font-mono">
                  {data.summary.active_projects} active
                </span>
              </div>
            </div>

            {/* Card 2: Total Ideas */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-2">
              <div className="flex items-center justify-between text-neutral-400">
                <span className="text-xs font-medium">Total Ideas</span>
                <Lightbulb className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-3xl font-bold text-white">
                {data.summary.total_ideas}
              </div>
              <div className="text-xs text-neutral-400 flex items-center justify-between pt-1">
                <span>Published vs Draft</span>
                <span className="text-neutral-300 font-mono">
                  {data.ideas.published} / {data.ideas.drafts}
                </span>
              </div>
            </div>

            {/* Card 3: Completed Evaluations */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-2">
              <div className="flex items-center justify-between text-neutral-400">
                <span className="text-xs font-medium">
                  Completed Evaluations
                </span>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-3xl font-bold text-white">
                {data.summary.completed_evaluations}
              </div>
              <div className="text-xs text-neutral-400 flex items-center justify-between pt-1">
                <span>Total Executions</span>
                <span className="text-neutral-300 font-mono">
                  {data.summary.total_evaluations}
                </span>
              </div>
            </div>

            {/* Card 4: Average Score */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-5 space-y-2">
              <div className="flex items-center justify-between text-neutral-400">
                <span className="text-xs font-medium">
                  Average Evaluation Score
                </span>
                <Award className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-3xl font-bold text-indigo-400">
                {data.summary.average_overall_score !== null
                  ? data.summary.average_overall_score
                  : "N/A"}
                {data.summary.average_overall_score !== null && (
                  <span className="text-sm font-normal text-neutral-400">
                    {" "}
                    / 100
                  </span>
                )}
              </div>
              <div className="text-xs text-neutral-400 flex items-center justify-between pt-1">
                <span>Criteria Standard</span>
                <span className="text-indigo-300 font-mono text-[11px]">
                  0 - 100 Scale
                </span>
              </div>
            </div>
          </div>

          {/* Time-Series Activity Trend (Pure SVG) */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-neutral-800 pb-3">
              <div>
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-indigo-400" />
                  <span>Activity & Creation Trends</span>
                </h3>
                <p className="text-xs text-neutral-400 mt-0.5">
                  Daily creation velocity for projects, ideas, and evaluations
                  over the selected range.
                </p>
              </div>

              {/* Chart Legend */}
              <div className="flex items-center gap-4 text-xs font-mono">
                <div className="flex items-center gap-1.5 text-indigo-400">
                  <div className="w-3 h-3 rounded-full bg-indigo-500" />
                  <span>Projects</span>
                </div>
                <div className="flex items-center gap-1.5 text-amber-400">
                  <div className="w-3 h-3 rounded-full bg-amber-500" />
                  <span>Ideas</span>
                </div>
                <div className="flex items-center gap-1.5 text-emerald-400">
                  <div className="w-3 h-3 rounded-full bg-emerald-500" />
                  <span>Evaluations</span>
                </div>
              </div>
            </div>

            {/* SVG Trend Visualization */}
            {data.trends.length === 0 ? (
              <div className="py-12 text-center text-xs text-neutral-500 italic">
                No activity trend records in selected date range.
              </div>
            ) : (
              <div className="space-y-4 pt-2">
                <div className="h-48 w-full flex items-end justify-between gap-2 border-b border-neutral-800 pb-2">
                  {data.trends.map((pt) => {
                    const maxVal = Math.max(
                      ...data.trends.map((t) =>
                        Math.max(
                          t.projects_count,
                          t.ideas_count,
                          t.evaluations_count,
                          1,
                        ),
                      ),
                    );

                    const pHeight = (pt.projects_count / maxVal) * 100;
                    const iHeight = (pt.ideas_count / maxVal) * 100;
                    const eHeight = (pt.evaluations_count / maxVal) * 100;

                    return (
                      <div
                        key={pt.date}
                        className="flex-1 flex items-end justify-center gap-1 group relative h-full"
                      >
                        {/* Tooltip */}
                        <div className="absolute -top-12 bg-neutral-800 text-[10px] text-neutral-200 p-2 rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10 whitespace-nowrap border border-neutral-700">
                          <div className="font-bold text-white mb-0.5">
                            {pt.date}
                          </div>
                          <div>Projects: {pt.projects_count}</div>
                          <div>Ideas: {pt.ideas_count}</div>
                          <div>Evaluations: {pt.evaluations_count}</div>
                        </div>

                        {/* Bar Segment: Projects */}
                        <div
                          className="w-2 bg-indigo-500 rounded-t transition-all duration-300 hover:bg-indigo-400"
                          style={{ height: `${Math.max(pHeight, 4)}%` }}
                        />
                        {/* Bar Segment: Ideas */}
                        <div
                          className="w-2 bg-amber-500 rounded-t transition-all duration-300 hover:bg-amber-400"
                          style={{ height: `${Math.max(iHeight, 4)}%` }}
                        />
                        {/* Bar Segment: Evaluations */}
                        <div
                          className="w-2 bg-emerald-500 rounded-t transition-all duration-300 hover:bg-emerald-400"
                          style={{ height: `${Math.max(eHeight, 4)}%` }}
                        />
                      </div>
                    );
                  })}
                </div>

                {/* X-Axis Date Labels */}
                <div className="flex justify-between text-[10px] font-mono text-neutral-500">
                  <span>{data.trends[0]?.date}</span>
                  {data.trends.length > 2 && (
                    <span>
                      {data.trends[Math.floor(data.trends.length / 2)]?.date}
                    </span>
                  )}
                  <span>{data.trends[data.trends.length - 1]?.date}</span>
                </div>
              </div>
            )}
          </div>

          {/* Detailed Metric Breakdowns Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Score Range Distribution */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
              <h3 className="text-base font-bold text-white border-b border-neutral-800 pb-3">
                Evaluation Score Range Distribution
              </h3>

              <div className="space-y-4 pt-1">
                {Object.entries(data.evaluations.score_distribution).map(
                  ([rangeKey, count]) => {
                    const totalCompleted = Math.max(
                      data.evaluations.completed,
                      1,
                    );
                    const pct = Math.round((count / totalCompleted) * 100);

                    return (
                      <div key={rangeKey} className="space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="font-mono text-neutral-300">
                            Score Range {rangeKey}
                          </span>
                          <span className="text-neutral-400 font-mono">
                            {count} evaluations ({pct}%)
                          </span>
                        </div>
                        <div className="w-full h-2 bg-neutral-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  },
                )}
              </div>
            </div>

            {/* Dimensional Averages */}
            <div className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
              <h3 className="text-base font-bold text-white border-b border-neutral-800 pb-3">
                Dimensional Averages Breakdown
              </h3>

              {Object.keys(data.evaluations.dimensional_averages).length ===
              0 ? (
                <div className="py-8 text-center text-xs text-neutral-500 italic">
                  Run evaluations to calculate criteria averages across
                  dimensions.
                </div>
              ) : (
                <div className="space-y-3 pt-1">
                  {Object.entries(data.evaluations.dimensional_averages).map(
                    ([dimKey, avgScore]) => (
                      <div key={dimKey} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="capitalize text-neutral-300 font-medium">
                            {dimKey.replace("_", " ")}
                          </span>
                          <span className="font-mono text-indigo-400 font-semibold">
                            {avgScore} / 100
                          </span>
                        </div>
                        <div className="w-full h-1.5 bg-neutral-800 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-400 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(avgScore, 100)}%` }}
                          />
                        </div>
                      </div>
                    ),
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
