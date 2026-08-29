"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import {
  ChevronDown,
  ArrowRight,
  Star,
  Compass,
  GitFork,
  Layers,
  FileCheck,
  Sliders,
  Menu,
  X,
  Lightbulb,
} from "lucide-react";
import { Show } from "@clerk/nextjs";
import { IdeaGPTLogo } from "../brand/IdeaGPTLogo";

function GithubIcon({ className = "w-4 h-4" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 24 24"
      width="24"
      height="24"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4" />
      <path d="M9 18c-4.51 2-5-2-7-2" />
    </svg>
  );
}

interface ResourceItem {
  title: string;
  desc: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
}

const learnResources: ResourceItem[] = [
  {
    title: "How IdeaGPT Works",
    desc: "Interactive 6-step deterministic pipeline.",
    href: "/#how-it-works",
    icon: Lightbulb,
    color: "text-amber-400 bg-amber-500/10 border-amber-500/20",
  },
  {
    title: "Strategy Lab & Frameworks",
    desc: "Scenario planning and risk modeling.",
    href: "/strategy-lab",
    icon: GitFork,
    color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/20",
  },
  {
    title: "Architecture & Blueprints",
    desc: "System designs and technical stacks.",
    href: "/architecture",
    icon: Layers,
    color: "text-purple-400 bg-purple-500/10 border-purple-500/20",
  },
];

const platformResources: ResourceItem[] = [
  {
    title: "Decision Reports",
    desc: "Executive summaries and audit outputs.",
    href: "/reports",
    icon: FileCheck,
    color: "text-emerald-400 bg-emerald-500/10 border-emerald-500/20",
  },
  {
    title: "GitHub Integration Lab",
    desc: "Repository validation and code intelligence.",
    href: "/github-lab",
    icon: GithubIcon,
    color: "text-blue-400 bg-blue-500/10 border-blue-500/20",
  },
  {
    title: "Platform Settings & BYOK",
    desc: "Model routing and provider keys.",
    href: "/settings",
    icon: Sliders,
    color: "text-teal-400 bg-teal-500/10 border-teal-500/20",
  },
];

export function LandingHeader() {
  const [resourcesOpen, setResourcesOpen] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [mobileResourcesOpen, setMobileResourcesOpen] = useState(false);

  const dropdownRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        triggerRef.current &&
        !triggerRef.current.contains(event.target as Node)
      ) {
        setResourcesOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Close on Escape key
  useEffect(() => {
    function handleKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setResourcesOpen(false);
        setMobileMenuOpen(false);
        triggerRef.current?.focus();
      }
    }
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, []);

  return (
    <header className="sticky top-0 z-50 w-full bg-[#070709]/90 backdrop-blur-md border-b border-zinc-800/70 px-4 sm:px-8 lg:px-12 py-3.5 transition-all">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Left: Brand Logo */}
        <Link
          href="/"
          className="focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] rounded-lg"
          aria-label="IdeaGPT Home"
        >
          <IdeaGPTLogo size="md" variant="compact" showSubtitle={false} />
        </Link>

        {/* Center: Desktop Navigation Links */}
        <nav
          className="hidden lg:flex items-center gap-6 xl:gap-8 text-xs font-semibold text-zinc-400"
          aria-label="Main Navigation"
        >
          <Link
            href="/#product"
            className="hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] rounded px-1.5 py-0.5"
          >
            Product
          </Link>
          <Link
            href="/#how-it-works"
            className="hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] rounded px-1.5 py-0.5"
          >
            How It Works
          </Link>
          <Link
            href="/#capabilities"
            className="hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] rounded px-1.5 py-0.5"
          >
            Capabilities
          </Link>
          <Link
            href="/strategy-lab"
            className="hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] rounded px-1.5 py-0.5"
          >
            Strategy
          </Link>
          <Link
            href="/#pricing"
            className="hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] rounded px-1.5 py-0.5"
          >
            Pricing
          </Link>

          {/* Resources Dropdown Trigger */}
          <div className="relative">
            <button
              ref={triggerRef}
              type="button"
              onClick={() => setResourcesOpen((prev) => !prev)}
              aria-expanded={resourcesOpen}
              aria-haspopup="true"
              aria-controls="resources-dropdown-menu"
              className={`flex items-center gap-1 transition-colors rounded px-1.5 py-0.5 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] ${
                resourcesOpen ? "text-[#00E5FF]" : "hover:text-white"
              }`}
            >
              <span>Resources</span>
              <ChevronDown
                className={`w-3.5 h-3.5 transition-transform duration-200 ${
                  resourcesOpen ? "rotate-180 text-[#00E5FF]" : "text-zinc-500"
                }`}
              />
            </button>

            {/* Resources Dropdown Menu Container */}
            {resourcesOpen && (
              <div
                id="resources-dropdown-menu"
                ref={dropdownRef}
                role="region"
                aria-label="Resources Menu"
                className="absolute top-full left-1/2 -translate-x-1/2 mt-3 w-[560px] rounded-2xl bg-[#0D0D10]/95 backdrop-blur-xl border border-zinc-800/90 shadow-[0_16px_48px_rgba(0,0,0,0.85)] p-5 z-50 animate-in fade-in-0 zoom-in-95 duration-150"
              >
                <div className="grid grid-cols-2 gap-5">
                  {/* Learn Column */}
                  <div>
                    <div className="text-[10px] font-mono font-bold tracking-widest text-zinc-400 uppercase mb-3 px-2">
                      LEARN & METHODOLOGY
                    </div>
                    <div className="space-y-1">
                      {learnResources.map((item) => {
                        const Icon = item.icon;
                        return (
                          <Link
                            key={item.title}
                            href={item.href}
                            onClick={() => setResourcesOpen(false)}
                            className="flex items-start gap-3 p-2 rounded-xl hover:bg-[#16161B] border border-transparent hover:border-zinc-800 transition-all group"
                          >
                            <div
                              className={`w-7 h-7 rounded-lg flex items-center justify-center border shrink-0 mt-0.5 ${item.color}`}
                            >
                              <Icon className="w-3.5 h-3.5" />
                            </div>
                            <div>
                              <div className="text-xs font-bold text-zinc-200 group-hover:text-white transition-colors">
                                {item.title}
                              </div>
                              <p className="text-[11px] text-zinc-400 leading-snug mt-0.5">
                                {item.desc}
                              </p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  </div>

                  {/* Platform Column */}
                  <div>
                    <div className="text-[10px] font-mono font-bold tracking-widest text-zinc-400 uppercase mb-3 px-2">
                      PLATFORM & VALIDATION
                    </div>
                    <div className="space-y-1">
                      {platformResources.map((item) => {
                        const Icon = item.icon;
                        return (
                          <Link
                            key={item.title}
                            href={item.href}
                            onClick={() => setResourcesOpen(false)}
                            className="flex items-start gap-3 p-2 rounded-xl hover:bg-[#16161B] border border-transparent hover:border-zinc-800 transition-all group"
                          >
                            <div
                              className={`w-7 h-7 rounded-lg flex items-center justify-center border shrink-0 mt-0.5 ${item.color}`}
                            >
                              <Icon className="w-3.5 h-3.5" />
                            </div>
                            <div>
                              <div className="text-xs font-bold text-zinc-200 group-hover:text-white transition-colors">
                                {item.title}
                              </div>
                              <p className="text-[11px] text-zinc-400 leading-snug mt-0.5">
                                {item.desc}
                              </p>
                            </div>
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </nav>

        {/* Right Actions: GitHub + Star, Sign In, Start Free */}
        <div className="flex items-center gap-3 sm:gap-4">
          {/* GitHub + Star Action */}
          <a
            href="https://github.com/Sarvadnya07/IdeaGPT"
            target="_blank"
            rel="noopener noreferrer"
            aria-label="Open IdeaGPT on GitHub"
            title="Open IdeaGPT on GitHub"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#141418] hover:bg-zinc-800 text-zinc-300 hover:text-white border border-zinc-800/90 hover:border-zinc-700 transition-all text-xs font-semibold group shadow-sm active:scale-95 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF]"
          >
            <GithubIcon className="w-3.5 h-3.5 text-zinc-400 group-hover:text-white transition-colors" />
            <span className="hidden sm:inline">GitHub</span>
            <span className="h-3 w-[1px] bg-zinc-800 mx-0.5 hidden sm:inline" />
            <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400/20 group-hover:fill-amber-400 transition-colors" />
            <span>Star</span>
          </a>

          {/* Authentication CTAs */}
          <Show when="signed-out">
            <Link
              href="/sign-in"
              className="text-xs font-semibold text-zinc-300 hover:text-white transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF] rounded px-1.5 py-1"
            >
              Sign In
            </Link>
            <Link
              href="/sign-up"
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_20px_rgba(0,229,255,0.35)] rounded-full transition-all active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#00E5FF]"
            >
              Start Free
            </Link>
          </Show>

          <Show when="signed-in">
            <Link
              href="/dashboard"
              className="flex items-center gap-1.5 px-4 py-2 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_20px_rgba(0,229,255,0.35)] rounded-full transition-all active:scale-95 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#00E5FF]"
            >
              Dashboard
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </Show>

          {/* Mobile Menu Toggle Button */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-expanded={mobileMenuOpen}
            aria-label="Toggle mobile menu"
            className="lg:hidden p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-zinc-800/80 transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[#00E5FF]"
          >
            {mobileMenuOpen ? (
              <X className="w-5 h-5" />
            ) : (
              <Menu className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Navigation */}
      {mobileMenuOpen && (
        <div className="lg:hidden fixed inset-x-0 top-[65px] bg-[#0A0A0D]/95 backdrop-blur-2xl border-b border-zinc-800/90 p-5 space-y-4 shadow-2xl z-50 animate-in slide-in-from-top-2 duration-200">
          <nav className="flex flex-col space-y-3 text-sm font-semibold text-zinc-300">
            <Link
              href="/#product"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-white py-1 transition-colors"
            >
              Product
            </Link>
            <Link
              href="/#how-it-works"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-white py-1 transition-colors"
            >
              How It Works
            </Link>
            <Link
              href="/#capabilities"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-white py-1 transition-colors"
            >
              Capabilities
            </Link>
            <Link
              href="/strategy-lab"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-white py-1 transition-colors"
            >
              Strategy
            </Link>
            <Link
              href="/#pricing"
              onClick={() => setMobileMenuOpen(false)}
              className="hover:text-white py-1 transition-colors"
            >
              Pricing
            </Link>

            {/* Mobile Resources Expandable Accordion */}
            <div className="pt-2 border-t border-zinc-800/80">
              <button
                type="button"
                onClick={() => setMobileResourcesOpen((prev) => !prev)}
                className="flex items-center justify-between w-full py-1 text-sm font-bold text-zinc-200 hover:text-white"
              >
                <span>Resources</span>
                <ChevronDown
                  className={`w-4 h-4 transition-transform duration-200 ${
                    mobileResourcesOpen ? "rotate-180 text-[#00E5FF]" : "text-zinc-500"
                  }`}
                />
              </button>

              {mobileResourcesOpen && (
                <div className="pl-2 pt-2 space-y-2">
                  <div className="text-[10px] font-mono font-bold text-zinc-400 uppercase tracking-widest mt-1">
                    LEARN
                  </div>
                  {learnResources.map((item) => (
                    <Link
                      key={item.title}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className="block text-xs text-zinc-300 hover:text-[#00E5FF] py-1 transition-colors"
                    >
                      {item.title}
                    </Link>
                  ))}
                  <div className="text-[10px] font-mono font-bold text-zinc-400 uppercase tracking-widest mt-2">
                    PLATFORM
                  </div>
                  {platformResources.map((item) => (
                    <Link
                      key={item.title}
                      href={item.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className="block text-xs text-zinc-300 hover:text-[#00E5FF] py-1 transition-colors"
                    >
                      {item.title}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </nav>

          {/* Mobile Auth & Actions */}
          <div className="pt-3 border-t border-zinc-800/80 flex flex-col gap-2.5">
            <Show when="signed-out">
              <Link
                href="/sign-in"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2 text-xs font-semibold text-zinc-300 hover:text-white bg-[#141418] border border-zinc-800 rounded-xl transition-all"
              >
                Sign In
              </Link>
              <Link
                href="/sign-up"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_15px_rgba(0,229,255,0.3)] rounded-xl transition-all"
              >
                Start Free
              </Link>
            </Show>
            <Show when="signed-in">
              <Link
                href="/dashboard"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full text-center py-2.5 text-xs font-bold text-zinc-950 bg-[#00E5FF] hover:bg-[#00D0E8] shadow-[0_0_15px_rgba(0,229,255,0.3)] rounded-xl transition-all"
              >
                Open Dashboard Workspace
              </Link>
            </Show>
          </div>
        </div>
      )}
    </header>
  );
}
