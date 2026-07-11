# Design System Inventory - Page Layouts

This document defines the structured layouts used to present data cleanly across all 16 page routing views of **IdeaGPT**.

---

## 🏛️ Layout Specifications

### 1. Unified Dashboard Shell (`/dashboard`)
- **Structure**: Two-column layout with a fixed Left Sidebar (`w-[260px] bg-[#0c0c0e]`) and a fluid Right Content Pane (`flex-1 flex flex-col`).
- **Main elements**:
  - Sticky Topbar Header (`h-16 bg-[#070709]/80 backdrop-blur-md`): Displays search, active title breadcrumbs, notifications, avatar widgets.
  - Middle Canvas container: Standard layout centering with unified margins.
  - Page Footer: copyright subtext on the left, GTM product/privacy links on the right.

### 2. Multi-column Dashboard grids
- **Triple Column Grid**: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6` (Used for displaying kpis and charts lists).
- **Split Editor Grid**: `grid grid-cols-1 lg:grid-cols-4 gap-6` (Used in Slide Pitch Deck and PRD generation; maps a 1-column checklist preview sidebar, 2-column main editor sheet, and 1-column copilot panel).

### 3. Split-screen Auth Gate (`/sign-in` & `/sign-up`)
- **Structure**: Two-column screen splits on desktop (`lg:flex`):
  - **Left Visual Column (`w-[45%] bg-[#09090b]`)**: Immersive dark canvas presenting glowing neural-network vectors, typography quotes, and founders info.
  - **Right Card Column (`flex-1 bg-[#070709]`)**: Center-aligned card holding Google/GitHub buttons, OR lines, input forms, and CTAs.
- **Mobile scale**: Left column drops, right column stretches to fill screen viewport.
