/**
 * Design Tokens - Shadows
 * Type-safe shadows, focus outlines, and glowing radial ambient effects for IdeaGPT
 */
export const shadows = {
  none: "none",
  sm: "0 1px 2px 0 rgba(0, 0, 0, 0.4)",
  md: "0 4px 6px -1px rgba(0, 0, 0, 0.5), 0 2px 4px -2px rgba(0, 0, 0, 0.5)",
  lg: "0 10px 15px -3px rgba(0, 0, 0, 0.6), 0 4px 6px -4px rgba(0, 0, 0, 0.6)",
  xl: "0 20px 25px -5px rgba(0, 0, 0, 0.7), 0 8px 10px -6px rgba(0, 0, 0, 0.7)",
  
  // Neon brand halos
  glow: {
    indigo: "0 0 15px rgba(99, 102, 241, 0.3)", // Primary glowing halo for badges & buttons
    purple: "0 0 15px rgba(168, 85, 247, 0.3)", // Secondary metrics glow
    success: "0 0 12px rgba(16, 185, 129, 0.25)", // Completed status dots
  },
} as const;

export type ShadowsType = typeof shadows;
