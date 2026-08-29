"use client";

import React, { use } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  BrainCircuit,
  Map,
  FileText,
  Settings,
} from "lucide-react";

export default function ProjectLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ slug: string }>;
}) {
  const pathname = usePathname();
  const { slug } = use(params);

  const navItems = [
    { name: "Overview", href: `/projects/${slug}`, icon: LayoutDashboard },
    {
      name: "AI Analysis",
      href: `/projects/${slug}/analysis`,
      icon: BrainCircuit,
    },
    { name: "Roadmap", href: `/projects/${slug}/roadmap`, icon: Map },
    { name: "Reports", href: `/projects/${slug}/reports`, icon: FileText },
    { name: "Settings", href: `/projects/${slug}/settings`, icon: Settings },
  ];

  return (
    <div className="space-y-6 py-4">
      <nav className="flex gap-2 border-b border-border/50 pb-4 overflow-x-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${
                isActive
                  ? "bg-indigo-500/10 text-indigo-400"
                  : "text-zinc-500 hover:text-white hover:bg-zinc-800/50"
              }`}
            >
              <Icon className="w-4 h-4" />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <main>{children}</main>
    </div>
  );
}
