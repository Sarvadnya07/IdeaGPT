# Design System Inventory - Reusable Components

This document catalogues the modular, reusable components designed across all 16 page routing views of the **IdeaGPT** SaaS workspace.

---

## 📦 Component Specifications

### 1. Button Variants

- **Primary CTA Button**: `bg-indigo-650 hover:bg-indigo-500 font-semibold text-white shadow-indigo` (GTM Share, Load Simulations).
- **Secondary Outlined Button**: `bg-[#0c0c0e] border border-zinc-800 hover:bg-zinc-800 text-zinc-300` (Export actions, edit triggers, files attachments).
- **Gradient Action Button**: `bg-gradient-to-r from-indigo-500 via-indigo-600 to-purple-600 hover:from-indigo-400 hover:to-purple-500` (Generate AI Analysis triggers, pitch refiners).

### 2. Glassmorphic Card Containers

- **Core Card Grid**: `bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-2xl backdrop-blur-md` (Used as the core dashboard widget envelope, featuring glowing radial gradients in the upper right).
- **Nested Card Node**: `bg-[#070709] border border-zinc-900/60 rounded-xl p-4 space-y-4` (Timelines cards, checklist lists, slide timelines, codeblock tabs).

### 3. Inputs & Form Controls

- **Standard Text Input**: `bg-[#070709] border border-zinc-800/80 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 rounded-xl px-4 py-3 text-xs` (Project titles, credentials, command palettes).
- **Standard Textarea**: `resize-none leading-relaxed min-h-[120px]` (Problem description, speaker notes, AI inputs).
- **Standard Selector**: `cursor-pointer font-medium px-4 py-3 text-xs bg-[#070709] border border-zinc-800/80 focus:border-indigo-500 rounded-xl` (Timeline filters, industry dropdowns).

### 4. Custom SVG Chart Wrappers

- **Doughnut Sizing Chart**: Circular SVG plotting multiple segments (`stroke-indigo-500`, `stroke-purple-500`, `stroke-zinc-800`) with dynamic center texts (TAM values).
- **Vector Area Line Chart**: Multi-line SVG area graph plotting load projections or revenue curves with indigo gradients fills (`url(#area-grad)`) and time footer nodes.
- **Topological Visual Nodes**: HTML connected node boxes mapped with SVG straight lines (`stroke-indigo-500`, `stroke-purple-500`).
