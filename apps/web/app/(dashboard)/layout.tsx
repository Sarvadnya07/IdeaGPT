import React from "react";
import { auth } from "@clerk/nextjs/server";
import { DashboardClientLayout } from "../../components/layout/DashboardClientLayout";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  await auth.protect();

  return <DashboardClientLayout>{children}</DashboardClientLayout>;
}
