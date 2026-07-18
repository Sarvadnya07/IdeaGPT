"use client";

import React, { useState } from "react";
import { toast } from "sonner";
import {
  Settings,
  Save,
  Shield,
  User,
  BellRing,
  Cpu,
  Palette,
  Globe,
  Keyboard,
  Accessibility,
  Check,
} from "lucide-react";

const PROVIDERS = ["openai", "gemini", "ollama", "mock"];
const MODELS: Record<string, string[]> = {
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
  gemini: ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
  ollama: ["llama3.2", "mistral", "phi3"],
  mock: ["mock-model"],
};
const LANGUAGES = ["English", "Spanish", "French", "German", "Japanese", "Chinese (Simplified)"];
const THEMES = ["Dark", "System"];

const SHORTCUT_MAP = [
  { action: "New Project", keys: "⌘ N" },
  { action: "Global Search", keys: "⌘ K" },
  { action: "Save", keys: "⌘ S" },
  { action: "Open Settings", keys: "⌘ ," },
  { action: "Navigate Dashboard", keys: "G D" },
  { action: "Navigate Analysis", keys: "G A" },
];

export default function SettingsPage() {
  const [profileName, setProfileName] = useState("David Chen");
  const [email, setEmail] = useState("david@stealthstartup.co");
  const [receiveAlerts, setReceiveAlerts] = useState(true);
  const [weeklyDigest, setWeeklyDigest] = useState(true);
  const [evaluationComplete, setEvaluationComplete] = useState(true);

  // AI defaults
  const [defaultProvider, setDefaultProvider] = useState("openai");
  const [defaultModel, setDefaultModel] = useState("gpt-4o");
  const [maxTokens, setMaxTokens] = useState("4096");
  const [temperature, setTemperature] = useState("0.7");

  // Theme & Language
  const [theme, setTheme] = useState("Dark");
  const [language, setLanguage] = useState("English");
  const [reducedMotion, setReducedMotion] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [largeText, setLargeText] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Settings updated successfully!");
  };

  const inputCls =
    "block w-full px-4 py-2.5 text-xs text-zinc-300 bg-[#070709] border border-zinc-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 rounded-xl outline-none transition-all font-medium";
  const selectCls =
    "block w-full px-4 py-2.5 text-xs text-zinc-300 bg-[#070709] border border-zinc-800 focus:border-indigo-500 rounded-xl outline-none transition-all font-medium";
  const sectionCls = "bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]";
  const sectionHeaderCls =
    "text-xs font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-5 flex items-center gap-2";
  const labelCls = "text-[10px] font-bold text-zinc-500 uppercase tracking-widest";

  const Toggle = ({
    value,
    onChange,
    label,
    desc,
  }: {
    value: boolean;
    onChange: (v: boolean) => void;
    label: string;
    desc?: string;
  }) => (
    <div className="flex items-center justify-between py-3 border-b border-zinc-900/40 last:border-0">
      <div>
        <p className="text-xs font-bold text-white">{label}</p>
        {desc && <p className="text-[10px] text-zinc-500 mt-0.5 font-medium">{desc}</p>}
      </div>
      <button
        type="button"
        onClick={() => onChange(!value)}
        className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors ${
          value ? "bg-indigo-600" : "bg-zinc-800"
        }`}
      >
        <span
          className={`inline-block h-3.5 w-3.5 rounded-full bg-white shadow-sm transition-transform ${
            value ? "translate-x-4" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );

  return (
    <div className="space-y-8 py-4 select-none max-w-4xl">
      {/* Title */}
      <div className="space-y-2 border-b border-zinc-900 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Settings className="w-5 h-5" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Settings</h1>
        </div>
        <p className="text-sm text-zinc-500 leading-relaxed">
          Manage your personal workspace preferences, AI defaults, notification rules, and security.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* ── Profile Card ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <User className="w-4 h-4 text-indigo-400" />
            Profile Credentials
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1.5">
              <label className={labelCls}>Full Name</label>
              <input
                type="text"
                value={profileName}
                onChange={(e) => setProfileName(e.target.value)}
                className={inputCls}
              />
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputCls}
              />
            </div>
          </div>
        </div>

        {/* ── AI Provider Defaults ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <Cpu className="w-4 h-4 text-purple-400" />
            AI Provider Defaults
          </h3>
          <p className="text-xs text-zinc-500 mb-5 -mt-2 leading-relaxed">
            Select which AI provider and model to use for new evaluations. You can always override per-evaluation.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1.5">
              <label className={labelCls}>Default Provider</label>
              <select
                value={defaultProvider}
                onChange={(e) => {
                  setDefaultProvider(e.target.value);
                  setDefaultModel(MODELS[e.target.value][0]);
                }}
                className={selectCls}
              >
                {PROVIDERS.map((p) => (
                  <option key={p} value={p}>
                    {p.charAt(0).toUpperCase() + p.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Default Model</label>
              <select
                value={defaultModel}
                onChange={(e) => setDefaultModel(e.target.value)}
                className={selectCls}
              >
                {MODELS[defaultProvider].map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Max Tokens</label>
              <input
                type="number"
                value={maxTokens}
                min={512}
                max={32768}
                onChange={(e) => setMaxTokens(e.target.value)}
                className={inputCls}
              />
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Temperature (0.0 – 1.0)</label>
              <input
                type="number"
                value={temperature}
                min={0}
                max={1}
                step={0.1}
                onChange={(e) => setTemperature(e.target.value)}
                className={inputCls}
              />
            </div>
          </div>

          {/* Provider health indicators */}
          <div className="mt-5 flex flex-wrap gap-2">
            {PROVIDERS.map((p) => (
              <div
                key={p}
                className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[9px] font-bold uppercase tracking-widest ${
                  p === defaultProvider
                    ? "bg-indigo-500/10 border-indigo-500/20 text-indigo-400"
                    : "bg-zinc-900/50 border-zinc-800 text-zinc-500"
                }`}
              >
                <span
                  className={`w-1.5 h-1.5 rounded-full ${p === "mock" ? "bg-zinc-600" : "bg-emerald-500"}`}
                />
                {p}
                {p === defaultProvider && <Check className="w-2.5 h-2.5" />}
              </div>
            ))}
          </div>
        </div>

        {/* ── Theme & Language ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <Palette className="w-4 h-4 text-pink-400" />
            Theme & Language
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className={labelCls}>Theme</label>
              <div className="flex gap-2">
                {THEMES.map((t) => (
                  <button
                    key={t}
                    type="button"
                    onClick={() => setTheme(t)}
                    className={`flex-1 py-2.5 text-[10px] font-bold rounded-xl border transition-all ${
                      theme === t
                        ? "bg-indigo-500/10 border-indigo-500/30 text-indigo-400"
                        : "bg-zinc-900/50 border-zinc-800 text-zinc-500 hover:border-zinc-700"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className={selectCls}
              >
                {LANGUAGES.map((l) => (
                  <option key={l} value={l}>
                    {l}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* ── Notifications ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <BellRing className="w-4 h-4 text-sky-400" />
            Notification Preferences
          </h3>
          <Toggle
            value={receiveAlerts}
            onChange={setReceiveAlerts}
            label="Evaluation Alerts"
            desc="Receive in-app alerts when an evaluation completes or fails."
          />
          <Toggle
            value={evaluationComplete}
            onChange={setEvaluationComplete}
            label="Email on Completion"
            desc="Send an email when AI evaluation finishes."
          />
          <Toggle
            value={weeklyDigest}
            onChange={setWeeklyDigest}
            label="Weekly Insights Digest"
            desc="Receive a weekly email with new recommendations across all projects."
          />
        </div>

        {/* ── Keyboard Shortcuts ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <Keyboard className="w-4 h-4 text-emerald-400" />
            Keyboard Shortcuts
          </h3>
          <div className="space-y-0">
            {SHORTCUT_MAP.map((s) => (
              <div
                key={s.action}
                className="flex items-center justify-between py-3 border-b border-zinc-900/40 last:border-0"
              >
                <span className="text-xs font-medium text-zinc-400">{s.action}</span>
                <div className="flex gap-1">
                  {s.keys.split(" ").map((key, i) => (
                    <kbd
                      key={i}
                      className="px-2 py-1 bg-zinc-900 border border-zinc-800 rounded text-[9px] font-bold text-zinc-400"
                    >
                      {key}
                    </kbd>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ── Accessibility ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <Accessibility className="w-4 h-4 text-orange-400" />
            Accessibility
          </h3>
          <Toggle
            value={reducedMotion}
            onChange={setReducedMotion}
            label="Reduce Motion"
            desc="Minimize animations and transitions across the interface."
          />
          <Toggle
            value={highContrast}
            onChange={setHighContrast}
            label="High Contrast Mode"
            desc="Increase border and text contrast for improved readability."
          />
          <Toggle
            value={largeText}
            onChange={setLargeText}
            label="Large Text"
            desc="Scale up base text size by 20% throughout the app."
          />
        </div>

        {/* ── Security ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <Shield className="w-4 h-4 text-red-400" />
            Security
          </h3>
          <div className="space-y-4">
            <button
              type="button"
              onClick={() => toast.success("Password reset email sent!")}
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors"
            >
              Change Password →
            </button>
            <div className="text-[10px] text-zinc-500">
              Last login: Today at 11:43 AM · Chrome · Windows 11
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="flex items-center gap-2 px-6 py-3 text-sm font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_20px_rgba(79,70,229,0.3)] rounded-xl transition-all active:scale-[0.98]"
          >
            <Save className="w-4 h-4" />
            Save Changes
          </button>
        </div>
      </form>
    </div>
  );
}
