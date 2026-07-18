"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { Menu, Search, Bell, BookOpen, Moon, Sun, User } from "lucide-react";
import { useTheme } from "next-themes";
import { UserButton, useAuth } from "@clerk/nextjs";
import { CommandPalette } from "../shared/CommandPalette";

interface TopNavProps {
  setMobileMenuOpen: (open: boolean) => void;
}

export function TopNav({ setMobileMenuOpen }: TopNavProps) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const { isLoaded, userId } = useAuth();

  const getSearchPlaceholder = () => {
    if (pathname.includes("roadmap")) return "Search milestones...";
    if (pathname.includes("tech-stack")) return "Search architecture...";
    if (pathname.includes("ai-analysis")) return "Search insights...";
    return "Search dashboard...";
  };

  const getPageTitle = () => {
    if (pathname.includes("ai-analysis")) return "Idea Analysis";
    if (pathname.includes("roadmap")) return "Implementation Roadmap";
    if (pathname.includes("tech-stack")) return "Tech Stack";
    if (pathname.includes("dashboard")) return "Dashboard Overview";
    return "Workspace";
  };

  return (
    <header className="sticky top-0 z-40 flex items-center justify-between h-16 px-6 md:px-8 bg-background/80 backdrop-blur-md border-b border-border">
      <div className="flex items-center gap-4 flex-1">
        <button
          onClick={() => setMobileMenuOpen(true)}
          className="lg:hidden p-2 -ml-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:block font-bold text-sm tracking-tight shrink-0">
          {getPageTitle()}
        </div>

        <div className="relative max-w-xs w-full ml-4 hidden md:block">
          <CommandPalette />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
        >
          <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute top-[1.35rem] right-[5.8rem] h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </button>

        <button className="relative p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors">
          <Bell className="w-4 h-4" />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
        </button>

        <button className="p-2 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted transition-colors">
          <BookOpen className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-2 pl-2">
          {!isLoaded ? (
            <div className="w-8 h-8 rounded-full border border-border bg-muted animate-pulse"></div>
          ) : userId ? (
            <UserButton afterSignOutUrl="/" />
          ) : (
            <button className="w-8 h-8 rounded-full border border-border bg-muted flex items-center justify-center text-xs font-bold text-muted-foreground hover:bg-muted/80 transition-colors">
              <User className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
