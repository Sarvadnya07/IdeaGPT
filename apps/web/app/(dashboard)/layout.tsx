import React from "react";
import { auth } from "@clerk/nextjs/server";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { DashboardClientLayout } from "../../components/layout/DashboardClientLayout";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  let isTestUser = false;
  if (process.env.NODE_ENV !== "production") {
    const cookieStore = await cookies();
    if (cookieStore.get("ideagpt_test_session")?.value) {
      isTestUser = true;
    }
  }

  if (!isTestUser) {
    const { userId } = await auth();
    if (!userId) {
      redirect("/sign-in");
    }
  }

  return <DashboardClientLayout>{children}</DashboardClientLayout>;
}
