"use client";

import React, { useState, useEffect } from "react";
import { toast } from "sonner";
import { useApiClient } from "@/lib/api/client";
import {
  Settings,
  Save,
  Shield,
  User as UserIcon,
  BellRing,
  Cpu,
  Palette,
  Keyboard,
  Accessibility,
  Check,
  Loader2,
  Lock,
} from "lucide-react";

interface UserData {
  id: number;
  clerk_id: string;
  email: string | null;
  name: string | null;
  full_name: string | null;
  avatar: string | null;
  role: string;
  timezone: string | null;
  locale: string | null;
}

const PROVIDERS = ["openai", "gemini", "ollama", "mock"];
const MODELS: Record<string, string[]> = {
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
  gemini: ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
  ollama: ["llama3.2", "mistral", "phi3"],
  mock: ["mock-model"],
};
const LANGUAGES = ["English", "Spanish", "French", "German", "Japanese"];
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
  const api = useApiClient();

  const [isLoadingUser, setIsLoadingUser] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  const [user, setUser] = useState<UserData | null>(null);
  const [profileName, setProfileName] = useState("");
  const [fullName, setFullName] = useState("");
  const [timezone, setTimezone] = useState("UTC");

  // Notifications
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

  // Fetch real user profile on mount
  useEffect(() => {
    async function loadUser() {
      try {
        const res = await api.get<UserData>("/users/me");
        setUser(res.data);
        setProfileName(res.data.name || "");
        setFullName(res.data.full_name || "");
        setTimezone(res.data.timezone || "UTC");
      } catch (err) {
        toast.error("Failed to load user profile");
      } finally {
        setIsLoadingUser(false);
      }
    }
    loadUser();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      // Save profile updates to FastAPI backend (email is identity-protected)
      const res = await api.patch<UserData>("/users/me", {
        name: profileName,
        full_name: fullName,
        timezone: timezone,
      });

      setUser(res.data);
      toast.success("Settings updated successfully!");
    } catch (err) {
      toast.error("Failed to update user profile.");
    } finally {
      setIsSaving(false);
    }
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

  if (isLoadingUser) {
    return (
      <div className="flex justify-center py-20">
        <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8 py-4 select-none max-w-4xl mx-auto">
      {/* Title */}
      <div className="space-y-2 border-b border-zinc-900 pb-6">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
            <Settings className="w-5 h-5" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Settings</h1>
        </div>
        <p className="text-sm text-zinc-500 leading-relaxed">
          Manage your authenticated profile, AI defaults, and notification preferences.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* ── Identity & Profile Card ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <UserIcon className="w-4 h-4 text-indigo-400" />
            Authenticated Profile
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1.5">
              <label className={labelCls}>Display Name</label>
              <input
                type="text"
                value={profileName}
                onChange={(e) => setProfileName(e.target.value)}
                placeholder="Your display name"
                className={inputCls}
              />
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your full name"
                className={inputCls}
              />
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Email Address (Clerk Verified Identity)</label>
              <div className="relative">
                <input
                  type="email"
                  disabled
                  value={user?.email || "No email claim"}
                  className="block w-full px-4 py-2.5 text-xs text-zinc-500 bg-zinc-900/50 border border-zinc-800/80 rounded-xl outline-none cursor-not-allowed font-medium pr-10"
                />
                <Lock className="w-3.5 h-3.5 text-zinc-600 absolute right-3 top-1/2 -translate-y-1/2" />
              </div>
            </div>
            <div className="space-y-1.5">
              <label className={labelCls}>Timezone</label>
              <input
                type="text"
                value={timezone}
                onChange={(e) => setTimezone(e.target.value)}
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
            Select which AI provider and model to use for new evaluations.
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
        </div>

        {/* ── Theme & Notifications ── */}
        <div className={sectionCls}>
          <h3 className={sectionHeaderCls}>
            <BellRing className="w-4 h-4 text-sky-400" />
            Notifications & Preferences
          </h3>
          <Toggle
            value={receiveAlerts}
            onChange={setReceiveAlerts}
            label="Evaluation Alerts"
            desc="Receive alerts when an evaluation completes or fails."
          />
          <Toggle
            value={evaluationComplete}
            onChange={setEvaluationComplete}
            label="Email Notifications"
            desc="Send email on evaluation completion."
          />
        </div>

        {/* Save Button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            disabled={isSaving}
            className="flex items-center gap-2 px-6 py-3 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 shadow-[0_0_20px_rgba(79,70,229,0.3)] rounded-xl transition-all active:scale-[0.98]"
          >
            {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Save Changes
          </button>
        </div>
      </form>
    </div>
  );
}
