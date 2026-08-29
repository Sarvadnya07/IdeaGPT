import React, { useEffect } from "react";
import { Search as SearchIcon } from "lucide-react";
import { useModal } from "@/providers/ModalProvider";

export function CommandPalette() {
  const { openModal } = useModal();

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        openModal(
          <div className="p-4 space-y-4 text-white">
            <h2 className="text-xl font-bold">Search Projects</h2>
            <input
              autoFocus
              className="w-full bg-zinc-900 border border-zinc-700 rounded p-3 focus:outline-none focus:border-indigo-500"
              placeholder="Type a command or search..."
            />
          </div>,
        );
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, [openModal]);

  return (
    <div
      onClick={() => {
        openModal(
          <div className="p-4 space-y-4 text-white">
            <h2 className="text-xl font-bold">Search Projects</h2>
            <input
              autoFocus
              className="w-full bg-zinc-900 border border-zinc-700 rounded p-3 focus:outline-none focus:border-indigo-500"
              placeholder="Type a command or search..."
            />
          </div>,
        );
      }}
      className="hidden md:flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-sm text-zinc-400 hover:text-zinc-300 hover:border-zinc-700 transition-colors cursor-pointer w-64"
    >
      <SearchIcon className="w-4 h-4" />
      <span>Search...</span>
      <kbd className="ml-auto hidden sm:inline-flex h-5 items-center gap-1 rounded border border-zinc-700 bg-zinc-800 px-1.5 font-mono text-[10px] font-medium text-zinc-400">
        <span className="text-xs">⌘</span>K
      </kbd>
    </div>
  );
}
