# Design System Inventory - Typography

This document defines the type scales, weights, and letter-spacings used in **IdeaGPT** to ensure enterprise-grade readability and visual hierarchy.

---

## ✒️ Typography Specifications

### 1. Typography Scales

- **Main Font Family**: `Plus Jakarta Sans`, `system-ui`, `sans-serif` (glorious geometric sans-serif loaded from `next/font/google`).
- **Monospace Code Family**: `font-mono`, `ui-monospace`, `Courier New` (YAML code block previews, editor terminals).

### 2. Heading Scales

- **H1 (Hero Heading)**: `text-5xl md:text-6xl lg:text-7xl font-black tracking-tight` (Hero branding, Landing page CTAs).
- **H2 (Page Title)**: `text-3xl md:text-4xl font-extrabold tracking-tight` (Dynamic AI Reports titles, PRD titles, comparative headings).
- **H3 (Section Title)**: `text-base font-bold tracking-normal` (Card headers, Kanban headers, node details).
- **H4 (Sub-Card Title)**: `text-xs font-bold tracking-tight` (Checklist labels, slide titles, sidebar options).

### 3. Body Text Scales

- **Standard Body**: `text-xs text-zinc-400 font-medium leading-relaxed` (Descriptions, user testimonials, AI recommendations).
- **Lowercase Label**: `text-[9px] font-bold text-zinc-600 uppercase tracking-widest` (Inputs labels, category heads, breadcrumbs).
- **Code Editor**: `text-[10px] leading-relaxed font-mono text-zinc-400` (Terminal specifications, code blocks).
