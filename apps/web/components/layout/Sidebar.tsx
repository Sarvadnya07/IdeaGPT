"use client";

import React from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Lightbulb,
  Map,
  Layers,
  Bookmark,
  Settings,
  Plus,
  Cpu,
  UserCheck,
  GitCompare,
  TrendingUp,
  Activity,
  FileText,
  Presentation,
  Boxes,
  Target,
  X,
  Sparkles,
} from "lucide-react";
import { cn } from "../../lib/utils";
import { IdeaGPTLogo } from "../brand/IdeaGPTLogo";

interface SidebarGroup {
  heading: string;
  items: {
    name: string;
    href: string;
    icon: React.ComponentType<any>;
    isComingSoon?: boolean;
  }[];
}

const navigationGroups: SidebarGroup[] = [
  {
    heading: "Core Workspace",
    items: [
      { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
      { name: "Idea Analysis", href: "/ai-analysis", icon: Lightbulb },
      { name: "Compare Ideas", href: "/compare", icon: GitCompare },
      { name: "Saved Reports", href: "/reports", icon: Bookmark },
    ],
  },
  {
    heading: "Evaluation Tools",
    items: [
      { name: "Roadmaps", href: "/roadmap", icon: Map },
      { name: "Tech Stacks", href: "/tech-stack", icon: Layers },
      { name: "PRD Generator", href: "/prd-generator", icon: FileText },
      { name: "Pitch Deck Gen", href: "/pitch-deck", icon: Presentation },
      { name: "Blueprint Studio", href: "/architecture", icon: Boxes },
    ],
  },
  {
    heading: "Simulations & Operations",
    items: [
      { name: "Platform Ops", href: "/analytics", icon: Activity },
      {
        name: "Investor Analysis",
        href: "/investor",
        icon: TrendingUp,
        isComingSoon: true,
      },
      { name: "AI Mentor", href: "/mentor", icon: Cpu, isComingSoon: true },
      {
        name: "Recruiter Sim",
        href: "/recruiter",
        icon: UserCheck,
        isComingSoon: true,
      },
      {
        name: "GitHub Lab",
        href: "/github-lab",
        icon: Cpu,
        isComingSoon: true,
      },
      {
        name: "Strategy Lab",
        href: "/strategy-lab",
        icon: Target,
        isComingSoon: true,
      },
    ],
  },
];

interface SidebarProps {
  mobileMenuOpen: boolean;
  setMobileMenuOpen: (open: boolean) => void;
}

export function Sidebar({ mobileMenuOpen, setMobileMenuOpen }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const activeHref = pathname.includes("ai-analysis")
    ? "/ai-analysis"
    : pathname;

  const handleNewAnalysis = () => {
    router.push("/ai-analysis");
    setMobileMenuOpen(false);
  };

  const SidebarContent = () => (
    <>
      <div className="p-5 border-b border-zinc-900/80 sticky top-0 bg-[#0c0c0e]/95 backdrop-blur-md z-10">
        <Link href="/dashboard" className="block focus:outline-none">
          <IdeaGPTLogo size="md" variant="full" />
        </Link>
      </div>

      <nav className="flex-1 px-4 py-6 space-y-6">
        {navigationGroups.map((group) => (
          <div key={group.heading} className="space-y-1.5">
            <span className="px-4 text-[9px] font-bold text-zinc-600 uppercase tracking-widest">
              {group.heading}
            </span>
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const isActive = activeHref === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={(e) => {
                      // if (item.isComingSoon) e.preventDefault();
                      setMobileMenuOpen(false);
                    }}
                    className={cn(
                      "flex items-center gap-3 px-4 py-2 text-xs font-semibold rounded-xl transition-all duration-200 group relative",
                      isActive
                        ? "bg-[#141417] text-white border-l-2 border-indigo-500 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]"
                        : "text-zinc-500 hover:text-zinc-300 hover:bg-[#0f0f12]",
                      item.isComingSoon && "opacity-60",
                    )}
                  >
                    <item.icon
                      className={cn(
                        "w-4 h-4 transition-transform duration-200 group-hover:scale-105",
                        isActive
                          ? "text-indigo-400"
                          : "text-zinc-500 group-hover:text-zinc-400",
                      )}
                    />
                    {item.name}
                    {item.isComingSoon && (
                      <span className="ml-auto text-[8px] uppercase tracking-widest bg-zinc-800 text-zinc-400 px-1.5 py-0.5 rounded font-bold">
                        Soon
                      </span>
                    )}
                    {isActive && !item.isComingSoon && (
                      <span className="absolute right-3 w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.6)]"></span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      <div className="p-4 border-t border-zinc-900/60 space-y-3 bg-[#0c0c0e] sticky bottom-0 z-10">
        <Link
          href="/settings"
          onClick={() => setMobileMenuOpen(false)}
          className={cn(
            "flex items-center gap-3 px-4 py-2.5 text-xs font-semibold rounded-xl transition-all duration-200 text-zinc-500 hover:text-zinc-300 hover:bg-[#0f0f12]",
            pathname === "/settings" &&
              "bg-[#141417] text-white border-l-2 border-indigo-500",
          )}
        >
          <Settings className="w-4 h-4 text-zinc-500" />
          Settings
        </Link>
        <button
          onClick={handleNewAnalysis}
          className="flex items-center justify-center gap-2 w-full px-4 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-[0.98] rounded-xl transition-all shadow-[0_4px_12px_rgba(79,70,229,0.3)]"
        >
          <Plus className="w-4 h-4 text-white" />
          New Project
        </button>
      </div>
    </>
  );

  return (
    <>
      <aside className="hidden lg:flex flex-col w-[260px] bg-[#0c0c0e] border-r border-zinc-900 shrink-0 select-none overflow-y-auto">
        <SidebarContent />
      </aside>

      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity"
            onClick={() => setMobileMenuOpen(false)}
          ></div>
          <div className="relative flex flex-col w-[260px] max-w-xs h-full bg-[#0c0c0e] border-r border-zinc-900 py-4 shadow-2xl animate-in slide-in-from-left duration-200 overflow-y-auto">
            <div className="absolute top-4 right-4 z-20">
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-1.5 rounded-lg text-zinc-400 hover:text-zinc-200 hover:bg-[#141417]"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <SidebarContent />
          </div>
        </div>
      )}
    </>
  );
}
