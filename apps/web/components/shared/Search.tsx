import React from "react";
import { Search as SearchIcon } from "lucide-react";

export function Search() {
  return (
    <div className="relative">
      <SearchIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
      <input 
        type="search" 
        placeholder="Search projects..." 
        className="w-full pl-10 pr-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-sm text-white focus:outline-none focus:border-indigo-500 transition-colors"
      />
    </div>
  );
}
