/**
 * Design Tokens - Colors
 * Unified color palette for IdeaGPT SaaS workspace
 */
export const colors = {
  // Base Canvas Colors
  background: {
    global: "#070709", // Deep Space Canvas background
    container: "#0c0c0e", // Sidebar, topbar, cards background
    card: "#0b0b0d", // Glassmorphism widgets background
    input: "#070709", // Form inputs background
  },

  // Muted Grays
  gray: {
    50: "#fafafa",
    100: "#f4f4f5",
    200: "#e4e4e7",
    300: "#d4d4d8",
    400: "#a1a1aa",
    500: "#71717a",
    600: "#52525b",
    700: "#3f3f46",
    800: "#27272a",
    900: "#18181b",
    950: "#09090b",
  },

  // Primary Indigo & Purple brand glow colors
  brand: {
    indigo: {
      400: "#818cf8",
      500: "#6366f1",
      600: "#4f46e5",
      700: "#4338ca",
    },
    purple: {
      400: "#c084fc",
      500: "#a855f7",
      600: "#9333ea",
    },
    fuchsia: {
      400: "#f472b6",
      500: "#ec4899",
    },
  },

  // Status Alerts colors
  status: {
    success: "#10b981", // Active state, checked options
    warning: "#f59e0b", // Middle risk, intermediate alerts
    error: "#ef4444", // Destructive blocks, timeouts, critical failures
    info: "#3b82f6", // General info labels
  },
} as const;

export type ColorsType = typeof colors;
