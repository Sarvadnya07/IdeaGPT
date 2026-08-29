/**
 * Design Tokens - Gradients
 * Type-safe brand background and linear gradients for IdeaGPT
 */
export const gradients = {
  // Brand Linear Gradients
  brand: {
    primary: "linear-gradient(to right, #4f46e5, #4338ca)", // Primary indigo button bg
    purple: "linear-gradient(to right, #6366f1, #a855f7)", // Standard analysis button bg
    fuchsia: "linear-gradient(to right, #a855f7, #ec4899)", // ARR, AI refine buttons bg
    neon: "linear-gradient(to tr, #4f46e5, #a855f7)", // Logo visual box bg
  },

  // Soft Radial Gradients for glow blurs
  ambient: {
    indigo:
      "radial-gradient(circle, rgba(79, 70, 229, 0.05) 0%, rgba(0, 0, 0, 0) 70%)", // Sidebar upper blurs
    purple:
      "radial-gradient(circle, rgba(168, 85, 247, 0.05) 0%, rgba(0, 0, 0, 0) 70%)", // Card hover blurs
  },
} as const;

export type GradientsType = typeof gradients;
