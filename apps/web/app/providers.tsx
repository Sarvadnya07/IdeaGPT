"use client";

import React, { createContext, useContext, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";
import { ThemeProvider } from "next-themes";
import { ModalProvider } from "../providers/ModalProvider";

// Mock idea context to prevent existing pages from breaking
interface IdeaData {
  title: string;
  problem: string;
  industry: string;
  timeline: string;
  potential: number;
}

interface IdeaContextType {
  idea: IdeaData;
  setIdea: (data: Partial<IdeaData>) => void;
  isAnalyzing: boolean;
  setIsAnalyzing: (val: boolean) => void;
}

const defaultIdea: IdeaData = {
  title: "",
  problem: "",
  industry: "",
  timeline: "",
  potential: 0,
};

const IdeaContext = createContext<IdeaContextType | undefined>(undefined);

export function useIdea() {
  const context = useContext(IdeaContext);
  if (!context) {
    throw new Error("useIdea must be used within an IdeaProvider");
  }
  return context;
}

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutes
            gcTime: 1000 * 60 * 15, // 15 minutes
            retry: 2,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: 1,
          },
        },
      }),
  );
  const [idea, setIdeaState] = useState<IdeaData>(defaultIdea);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const setIdea = (data: Partial<IdeaData>) => {
    setIdeaState((prev) => ({ ...prev, ...data }));
  };

  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem
      disableTransitionOnChange
    >
      <QueryClientProvider client={queryClient}>
        <IdeaContext.Provider
          value={{ idea, setIdea, isAnalyzing, setIsAnalyzing }}
        >
          <ModalProvider>
            {children}
            <Toaster
              theme="system"
              position="top-right"
              closeButton
              richColors
            />
          </ModalProvider>
        </IdeaContext.Provider>
      </QueryClientProvider>
    </ThemeProvider>
  );
}
