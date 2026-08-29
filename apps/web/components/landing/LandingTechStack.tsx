import React from "react";
import { Layers, Database, Cpu, Lock, Sparkles, Server } from "lucide-react";

export function LandingTechStack() {
  const technologies = [
    {
      name: "Next.js",
      badge: "N",
      badgeClass: "bg-black text-white border-zinc-700",
      description: "App Router & SSR",
    },
    {
      name: "TypeScript",
      badge: "TS",
      badgeClass: "bg-[#3178C6]/20 text-[#3178C6] border-[#3178C6]/40",
      description: "Strict Typed Schemas",
    },
    {
      name: "FastAPI",
      badge: "⚡",
      badgeClass: "bg-[#009688]/20 text-[#009688] border-[#009688]/40",
      description: "Async Python Engine",
    },
    {
      name: "PostgreSQL",
      badge: "🐘",
      badgeClass: "bg-[#336791]/20 text-[#336791] border-[#336791]/40",
      description: "Relational Knowledge Store",
    },
    {
      name: "Redis",
      badge: "🔴",
      badgeClass: "bg-[#DC382D]/20 text-[#DC382D] border-[#DC382D]/40",
      description: "Low-Latency Cache",
    },
    {
      name: "Clerk",
      badge: "C",
      badgeClass: "bg-[#6C47FF]/20 text-[#6C47FF] border-[#6C47FF]/40",
      description: "Multi-Tenant Auth",
    },
  ];

  return (
    <div className="w-full max-w-7xl mx-auto py-10 px-4 sm:px-8">
      <div className="rounded-2xl bg-[#0D0D10]/80 border border-zinc-800/80 p-6 sm:p-8 flex flex-col md:flex-row items-center justify-between gap-6">
        {/* Left text */}
        <div className="text-left">
          <h3 className="text-base sm:text-lg font-extrabold text-white tracking-tight">
            Built with Modern Technology.{" "}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-[#00C29A] to-[#0284C7]">
              Designed for Scale.
            </span>
          </h3>
          <p className="text-xs text-zinc-400 mt-1">
            Enterprise-grade multi-agent architecture with deterministic execution harnesses.
          </p>
        </div>

        {/* Right technology badges */}
        <div className="flex flex-wrap items-center justify-center md:justify-end gap-3 sm:gap-4">
          {technologies.map((tech) => (
            <div
              key={tech.name}
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#141418] border border-zinc-800/80 hover:border-zinc-700 transition-all group"
            >
              <div
                className={`w-6 h-6 rounded-md flex items-center justify-center font-mono font-bold text-xs border ${tech.badgeClass}`}
              >
                {tech.badge}
              </div>
              <span className="text-xs font-bold text-zinc-200 group-hover:text-white transition-colors">
                {tech.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
