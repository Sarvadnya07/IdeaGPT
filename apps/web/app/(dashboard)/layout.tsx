"use client";

import React, { useState } from "react";
import { Sidebar } from "../../components/layout/Sidebar";
import { TopNav } from "../../components/layout/TopNav";
import { PageContainer } from "../../components/layout/PageContainer";

export default function DashboardLayout({
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
