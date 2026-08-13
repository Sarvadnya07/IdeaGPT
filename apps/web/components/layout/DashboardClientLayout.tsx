"use client";

import React, { useState } from "react";
import { Sidebar } from "./Sidebar";
import { TopNav } from "./TopNav";
import { PageContainer } from "./PageContainer";

export function DashboardClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-background text-foreground font-sans overflow-x-hidden">
      <Sidebar 
        mobileMenuOpen={mobileMenuOpen} 
        setMobileMenuOpen={setMobileMenuOpen} 
      />
      <div className="flex-1 flex flex-col min-w-0 min-h-screen">
        <TopNav setMobileMenuOpen={setMobileMenuOpen} />
        <PageContainer>
          {children}
        </PageContainer>
      </div>
    </div>
  );
}
