# Design System Inventory - Animations & Polish

This document defines standard easing curves, hover transitions, loaders, and Framer Motion behaviors to enhance the user experience.

---

## ⚡ Animation Specifications

### 1. Easing Curves & Transitions
- **Standard Transition**: `transition-all duration-200 ease-in-out` (Sidebars links hover, buttons scaling, dropdown selections).
- **Scale micro-interaction**: `active:scale-[0.98]` or `active:scale-95` (Adds tactile feedback to clicks).

### 2. Multi-stage Loading States
- **AI Generator Loading**: Large circular pulse animation (`animate-ping`) combined with an active spinner (`animate-spin`), cycling through step-by-step texts.
- **Progress progression**: Easing transitions (`duration-700 ease-out`) applied to progress bar fills to animate from `0%` to target values.

### 3. Glow and Hover halos
- **Pulsing Halo**: Muted glowing ring indicators (`bg-indigo-400 animate-pulse` or `shadow-[0_0_8px_rgba(99,102,241,0.6)]`) for active status indicators.
- **Chart Area transitions**: Area-gradients utilizing soft fades to reveal curves gradually during viewport entry.
