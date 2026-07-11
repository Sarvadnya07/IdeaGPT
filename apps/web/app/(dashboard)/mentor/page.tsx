"use client";

import React, { useState } from "react";
import {
  Cpu,
  Search,
  ChevronRight,
  Sparkles,
  Database,
  Terminal,
  Activity,
  CheckCircle,
  FileCode,
  AlertTriangle,
  Play,
  ArrowRight,
  Send,
  Paperclip,
} from "lucide-react";
import { toast } from "sonner";

export default function MentorPage() {
  const [chatInput, setChatInput] = useState("");
  const [redisChecked, setRedisChecked] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput) return;
    toast.promise(
      new Promise((resolve) => setTimeout(resolve, 1500)),
      {
        loading: "AI Mentor is analyzing architectural patterns...",
        success: "Advice generated: Consider configuring a read-replica for high read scale.",
        error: "Failed to generate advice",
      }
    );
    setChatInput("");
  };

  return (
    <div className="space-y-8 py-4 select-none">
      {/* Search Header row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
        <div className="space-y-1.5">
          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block">
            AI Mentor Workspace
          </span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Project Titan Workspace
          </h1>
        </div>

        <div className="relative max-w-xs w-full">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-zinc-500" />
          </div>
          <input
            type="text"
            placeholder="Search knowledge base..."
            className="block w-full pl-9 pr-8 py-1.5 text-xs text-zinc-300 bg-[#0e0e11] border border-zinc-800 focus:border-indigo-500 rounded-lg outline-none transition-all placeholder:text-zinc-600"
          />
          <span className="absolute right-2.5 top-2 px-1 py-0.5 text-[8px] font-bold text-zinc-600 bg-zinc-900 border border-zinc-800 rounded">
            ⌘K
          </span>
        </div>
      </div>

      {/* Main Core Section Title */}
      <div className="bg-gradient-to-r from-indigo-950/20 via-zinc-950/40 to-zinc-950/20 border border-zinc-900/60 rounded-2xl p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-[200px] h-[200px] bg-indigo-500/[0.02] blur-[80px] pointer-events-none"></div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-widest">
                Active Strategy Context
              </span>
              <span className="inline-flex items-center px-2 py-0.5 rounded text-[8px] font-bold bg-green-500/10 border border-green-500/20 text-green-400 uppercase tracking-wider">
                Phase 1 Active
              </span>
            </div>
            <h2 className="text-xl font-extrabold text-white">
              Validating Core Architecture
            </h2>
            <p className="text-xs text-zinc-500 max-w-xl leading-relaxed">
              Based on your latest inputs regarding user scale, we need to finalize the caching layer before moving to frontend.
            </p>
          </div>
        </div>
      </div>

      {/* Workspace Grid content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Columns: Kanban and Codeblock */}
        <div className="lg:col-span-2 space-y-6">
          {/* Milestone Tracking Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3 mb-5">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Activity className="w-4 h-4 text-indigo-400" />
                Milestone Tracking
              </h3>
              <button className="text-[9px] font-bold text-indigo-400 hover:text-indigo-300 transition-colors uppercase tracking-widest">
                View All
              </button>
            </div>

            {/* Kanban Columns */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Column 1: Planned */}
              <div className="space-y-3 bg-[#070709] border border-zinc-900/60 rounded-xl p-3.5 min-h-[220px]">
                <div className="flex items-center justify-between border-b border-zinc-900/40 pb-2 mb-3">
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                    Planned (2)
                  </span>
                </div>

                {/* Card 1 */}
                <div className="bg-[#0c0c0e] border border-zinc-800 rounded-lg p-3 space-y-2 hover:border-zinc-700 transition-colors cursor-pointer">
                  <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-extrabold bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 uppercase tracking-wide">
                    Database
                  </span>
                  <h4 className="text-xs font-bold text-white">Design Schema for Auth</h4>
                  <div className="flex justify-between text-[9px] font-semibold text-zinc-600">
                    <span>Y1</span>
                    <span>Est. 3d</span>
                  </div>
                </div>

                {/* Card 2 */}
                <div className="bg-[#0c0c0e] border border-zinc-800 rounded-lg p-3 space-y-2 hover:border-zinc-700 transition-colors cursor-pointer">
                  <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-extrabold bg-purple-500/10 border border-purple-500/20 text-purple-400 uppercase tracking-wide">
                    API
                  </span>
                  <h4 className="text-xs font-bold text-white">REST Endpoint definition</h4>
                </div>
              </div>

              {/* Column 2: In Progress */}
              <div className="space-y-3 bg-[#070709] border border-zinc-900/60 rounded-xl p-3.5 min-h-[220px]">
                <div className="flex items-center justify-between border-b border-zinc-900/40 pb-2 mb-3">
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                    In Progress (1)
                  </span>
                </div>

                {/* Card 3 */}
                <div className="bg-[#0c0c0e] border border-zinc-800 rounded-lg p-3 space-y-2 hover:border-zinc-700 transition-colors cursor-pointer relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-1.5 h-full bg-orange-500"></div>
                  <span className="inline-block px-1.5 py-0.5 rounded text-[8px] font-extrabold bg-orange-500/10 border border-orange-500/20 text-orange-400 uppercase tracking-wide">
                    Infra
                  </span>
                  <h4 className="text-xs font-bold text-white">Setup Redis Cluster</h4>
                  <div className="flex justify-between text-[9px] font-semibold text-orange-400/80">
                    <span>High</span>
                    <span>Blocked &lt; 1d</span>
                  </div>
                </div>
              </div>

              {/* Column 3: Completed */}
              <div className="space-y-3 bg-[#070709] border border-zinc-900/60 rounded-xl p-3.5 min-h-[220px]">
                <div className="flex items-center justify-between border-b border-zinc-900/40 pb-2 mb-3">
                  <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                    Completed (2)
                  </span>
                </div>

                {/* Card 4 */}
                <div className="bg-[#0c0c0e] border border-zinc-850 rounded-lg p-3 space-y-1.5 opacity-60 hover:opacity-85 transition-opacity cursor-pointer">
                  <span className="text-[8px] font-extrabold text-green-400 uppercase tracking-wide block">
                    Doc
                  </span>
                  <h4 className="text-xs font-bold text-zinc-400 line-through">Project-scoping Doc</h4>
                  <span className="text-[9px] text-green-400 font-semibold flex items-center gap-1">
                    <CheckCircle className="w-3 h-3 text-green-400" />
                    Approved
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Architecture Proposal Card */}
          <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
              <FileCode className="w-4 h-4 text-purple-400" />
              Architecture Proposal
            </h3>

            <div className="space-y-4">
              <div className="flex items-center justify-between bg-zinc-950 border border-zinc-900 rounded-xl px-4 py-2 text-[10px] font-bold text-zinc-400">
                <span className="flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-zinc-500" />
                  docker-compose.yml
                </span>
                <span className="text-[8px] text-zinc-600 font-medium">YAML Preview</span>
              </div>

              {/* YAML Code Box */}
              <div className="bg-zinc-950 rounded-xl p-4 border border-zinc-900/80 font-mono text-[10px] text-zinc-400 overflow-x-auto leading-relaxed">
                <div className="text-indigo-400">version: <span className="text-zinc-100">&apos;3.8&apos;</span></div>
                <div className="text-indigo-400">services:</div>
                <div className="pl-4 text-indigo-400">redis-cluster:</div>
                <div className="pl-8 text-indigo-400">image: <span className="text-emerald-400">redis:7.0-alpine</span></div>
                <div className="pl-8 text-indigo-400">command: <span className="text-emerald-400">redis-server --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000 --appendonly yes</span></div>
                <div className="pl-8 text-indigo-400">ports:</div>
                <div className="pl-12 text-emerald-400">- &quot;6379:6379&quot;</div>
                <div className="pl-8 text-indigo-400">volumes:</div>
                <div className="pl-12 text-emerald-400">- redis_data:/data</div>
              </div>

              {/* Glowing Note Box */}
              <div className="bg-indigo-500/5 border border-indigo-500/10 rounded-xl p-4 flex items-start gap-2.5 text-[10.5px] text-zinc-400 leading-relaxed">
                <Sparkles className="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
                <p>
                  I suggest using Alpine for a smaller attack surface. Ensure persistent volumes are configured for cluster recovery.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: AI Guidance Copilot */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-5 shadow-[0_4px_24px_rgba(0,0,0,0.4)] flex flex-col justify-between min-h-[500px]">
          <div className="space-y-6">
            {/* Card Header */}
            <div className="flex items-center justify-between border-b border-zinc-900/60 pb-3 mb-2">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <Cpu className="w-4.5 h-4.5 text-indigo-400" />
                AI Guidance Copilot
              </h3>
              <span className="text-[8px] font-bold text-zinc-500 bg-zinc-900 border border-zinc-800 px-2 py-0.5 rounded uppercase tracking-wider">
                Architecture Context
              </span>
            </div>

            {/* Alert bottleneck box */}
            <div className="bg-red-500/5 border border-red-500/10 rounded-xl p-4 space-y-4">
              <div className="flex items-start gap-2 text-xs font-bold text-red-400 uppercase tracking-wide">
                <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                Potential Bottleneck Detected
              </div>
              <p className="text-[11px] text-zinc-500 leading-relaxed font-medium">
                Reviewing the kanban, &quot;Setup Redis Cluster&quot; has been in progress for 2 days. The blocker notes mention IAM roles. Should I generate the required AWS CloudFormation template for the exact IAM policies needed?
              </p>
              <button
                onClick={() => toast.success("IAM policies template generated!")}
                className="w-full py-2.5 text-[9px] font-bold text-zinc-300 bg-zinc-900 border border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700 rounded-lg uppercase tracking-widest active:scale-95 transition-all"
              >
                Generate IAM Template
              </button>
            </div>

            {/* Next logical actions checklist */}
            <div className="space-y-3.5 border-t border-zinc-900/60 pt-4">
              <span className="text-[9px] font-bold text-zinc-500 uppercase tracking-widest block">
                Next Logical Actions
              </span>
              {/* Checkbox 1 */}
              <div
                onClick={() => {
                  setRedisChecked(!redisChecked);
                  toast.success("Action updated!");
                }}
                className="flex items-start gap-3 cursor-pointer select-none py-1 group"
              >
                <div className={`w-4 h-4 border rounded shrink-0 mt-0.5 flex items-center justify-center transition-all ${
                  redisChecked ? "bg-indigo-600 border-indigo-500 text-white" : "border-zinc-800 group-hover:border-zinc-600 text-transparent"
                }`}>
                  <CheckCircle className="w-3.5 h-3.5" />
                </div>
                <div className="space-y-0.5">
                  <h4 className={`text-xs font-bold text-white ${redisChecked && "line-through text-zinc-600"}`}>
                    Review Redis Node Config
                  </h4>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                    Verify port mapping in docker-compose.
                  </p>
                </div>
              </div>

              {/* Checkbox 2 */}
              <div
                onClick={() => {
                  setAuthChecked(!authChecked);
                  toast.success("Action updated!");
                }}
                className="flex items-start gap-3 cursor-pointer select-none py-1 group"
              >
                <div className={`w-4 h-4 border rounded shrink-0 mt-0.5 flex items-center justify-center transition-all ${
                  authChecked ? "bg-indigo-600 border-indigo-500 text-white" : "border-zinc-800 group-hover:border-zinc-600 text-transparent"
                }`}>
                  <CheckCircle className="w-3.5 h-3.5" />
                </div>
                <div className="space-y-0.5">
                  <h4 className={`text-xs font-bold text-white ${authChecked && "line-through text-zinc-600"}`}>
                    Draft Auth Schema
                  </h4>
                  <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                    Based on Cognito requirements.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Interactive Chat Input Area at bottom */}
          <form onSubmit={handleSend} className="space-y-2 border-t border-zinc-900/60 pt-4 mt-6">
            <div className="relative flex items-center">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Ask for architectural advice..."
                className="block w-full pl-3 pr-16 py-2.5 text-xs text-zinc-300 bg-[#070709] border border-zinc-850 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 rounded-xl outline-none transition-all placeholder:text-zinc-600"
              />
              <div className="absolute right-2 flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => toast.success("File attached!")}
                  className="p-1 rounded-md text-zinc-600 hover:text-zinc-400"
                >
                  <Paperclip className="w-4.5 h-4.5" />
                </button>
                <button
                  type="submit"
                  className="p-1 rounded-md bg-indigo-600 text-white hover:bg-indigo-500"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
