import React from "react";
import { Loader2 } from "lucide-react";

export function LoadingState({ message = "Loading..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-12 min-h-[50vh]">
      <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mb-4" />
      <p className="text-zinc-400 text-sm">{message}</p>
    </div>
  );
}
