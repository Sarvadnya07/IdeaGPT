/**
 * Design Tokens - Typography
 * Unified font scales, font weights, and letter spacings for IdeaGPT
 */
export const typography = {
  fontFamily: {
    sans: "var(--font-sans), system-ui, sans-serif",
    mono: "var(--font-mono), monospace",
  },
  fontSize: {
    xs: "10px", // Uppercase small tags, sub-metrics labels
    sm: "12px", // General body text descriptions, checklist notes
    base: "14px", // Sidebar menus options, subheadings
    lg: "16px", // Card titles, section headers
    xl: "20px", // Intermediate metric totals
    "2xl": "24px", // Block headings, Series A titles
    "3xl": "30px", // Major page headings (New Idea Submission)
    "4xl": "36px", // Large metrics totals (arr projection, confidence score)
    "5xl": "48px", // Landing hero texts
  },
  fontWeight: {
    medium: "500", // Standard body weight
    semibold: "600", // Secondary options
    bold: "700", // Heading weight
    extrabold: "800", // Page title weights
    black: "900", // Huge metrics and Hero tags weight
  },
  letterSpacing: {
    tighter: "-0.05em",
    tight: "-0.025em",
    normal: "0em",
    wide: "0.025em",
    widest: "0.1em", // Small uppercase tags tracking
  },
} as const;

export type TypographyType = typeof typography;
