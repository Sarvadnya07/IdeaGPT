import {ClerkProvider} from "@clerk/nextjs";
import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "IdeaGPT - AI-Powered Project Analysis & Roadmapping",
  description: "Analyze market fit, technical feasibility, and generate standard roadmap timelines using advanced AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${jakarta.variable} dark`} suppressHydrationWarning>
      <body className="font-sans antialiased bg-[#070709] text-zinc-100 min-h-screen selection:bg-indigo-500/30 selection:text-white" suppressHydrationWarning>
        <ClerkProvider>
          <Providers>{children}</Providers>
        </ClerkProvider>
      </body>
    </html>
  );
}