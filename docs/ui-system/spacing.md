# Design System Inventory - Spacing & Grids

This document defines the spacing intervals, padding, margins, gaps, and responsive container guidelines for **IdeaGPT**.

---

## 📐 Spacing & Grid Specifications

### 1. Spacing Mappings
- **xs (Extra Small)**: `px-1.5 py-0.5` or `gap-1.5` (Status badges, small dots, user icons).
- **sm (Small)**: `px-3.5 py-1.5` or `gap-3` (Header icons, minor widgets, dropdown selectors).
- **md (Medium)**: `px-4.5 py-2.5` or `space-y-4` (Lists spacing, slide card spacing, checklist margins).
- **lg (Large)**: `px-6 py-6` or `gap-6` (Form widgets, dashboard grids, card margins).
- **xl (Extra Large)**: `px-8 py-8` or `space-y-8` (Core page margins, headers row, GTM grids).

### 2. Spacing Layout Containers
- **Main Shell Margins**: `max-w-7xl w-full mx-auto p-6 md:p-8` (Ensures that the content wraps perfectly on wide screens while maintaining a clean gutter on tablets and mobile screens).
- **Page Headings gutter**: `pb-6 border-b border-zinc-900 mb-8` (Standardized page title separation).

### 3. Responsive Breakpoints
- **Mobile (< 640px)**: Sidebar hidden, hamburger menu triggers collapsible drawer, grid cols collapse to `grid-cols-1`.
- **Tablet (640px - 1024px)**: Sidebar hidden, top navbar utility visible, grid cols expand to `grid-cols-2`.
- **Desktop (> 1024px)**: Left Sidebar fixed, main content layout expands, grids expand to `grid-cols-3` or `grid-cols-4` for slide reviews.
