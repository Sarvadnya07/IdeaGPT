"use client";

import React from "react";
import Link from "next/link";

export function PageContainer({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex-1 p-6 md:p-8 flex flex-col justify-between max-w-7xl w-full mx-auto">
      <div className="w-full">{children}</div>

      <footer className="mt-16 pt-8 border-t border-border flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
        <div>
          <span className="font-bold text-sm tracking-tight mr-2">IdeaGPT</span>
          © {new Date().getFullYear()} IdeaGPT AI. All rights reserved.
        </div>
        <div className="flex items-center gap-6 font-medium">
          <Link href="#" className="hover:text-foreground transition-colors">
            Product
          </Link>
          <Link href="#" className="hover:text-foreground transition-colors">
            API
          </Link>
          <Link href="#" className="hover:text-foreground transition-colors">
            Privacy
          </Link>
          <Link href="#" className="hover:text-foreground transition-colors">
            Terms
          </Link>
        </div>
      </footer>
    </main>
  );
}
