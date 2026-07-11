/**
 * Design Tokens - Radius
 * Unified card corner roundness profiles for IdeaGPT
 */
export const radius = {
  none: "0px",
  sm: "4px", // Minor status tags corners
  md: "8px", // Visual search fields, indicators, badge lists
  lg: "12px", // Nested cards (slide timeline items, timeline cards)
  xl: "16px", // Core widgets (metrics boxes, chart envelopes, forms)
  xxl: "24px", // Extra large sheets, authentication login blocks
  full: "9999px", // Rounded pills, avatar rings
} as const;

export type RadiusType = typeof radius;
