/**
 * Design Tokens - Animations
 * Type-safe easing curves, transition durations, and framer-motion delay intervals for IdeaGPT
 */
export const animations = {
  // Transition Easing curves
  easing: {
    standard: "cubic-bezier(0.4, 0, 0.2, 1)",
    decelerate: "cubic-bezier(0.0, 0, 0.2, 1)",
    accelerate: "cubic-bezier(0.4, 0, 1, 1)",
  },

  // Easing transition durations
  duration: {
    fast: "150ms", // Icon flips, minor scales
    normal: "200ms", // Sidebar link selection background swaps
    slow: "300ms", // Slide timeline swaps, sheet expansions
    long: "700ms", // Progress progression fills
  },

  // Easing delay intervals (sec) for stagger motions
  delay: {
    stagger: 0.05,
    initial: 0.1,
  },
} as const;

export type AnimationsType = typeof animations;
export const index = {
  colors: "./colors",
  spacing: "./spacing",
  radius: "./radius",
  typography: "./typography",
  shadows: "./shadows",
  gradients: "./gradients",
  animations: "./animations",
};
export const indexTsContent = `export * from "./colors";
export * from "./spacing";
export * from "./radius";
export * from "./typography";
export * from "./shadows";
export * from "./gradients";
export * from "./animations";
`;
