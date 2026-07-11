/**
 * Design Tokens - Spacing
 * Unified spacing grid intervals (padding, margins, gaps) for IdeaGPT
 */
export const spacing = {
  none: "0px",
  xs: "4px", // Extra small padding, badges, spacing
  sm: "8px", // Minor icons, dropdown items
  md: "12px", // Timelines lists spacing, slide timeline cards
  lg: "16px", // Card padding, standard grid elements gutter
  xl: "24px", // Large grids, forms gaps
  xxl: "32px", // Outer main container page margins
  huge: "48px", // Section gaps, main hero paddings
} as const;

export type SpacingType = typeof spacing;
