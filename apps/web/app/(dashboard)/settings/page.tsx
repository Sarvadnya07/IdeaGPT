"use client";

import React, { useState, useEffect } from "react";
import { toast } from "sonner";
import { useApiClient } from "@/lib/api/client";
import { useAICredentials } from "../../../hooks/useAICredentials";
import { useAIProviders } from "../../../hooks/useAIProviders";
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
  KeyRound,
  Trash2,
  CheckCircle2,
  AlertCircle,
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

const PROVIDERS = ["groq", "gemini", "openai", "ollama", "tavily"];
const MODELS: Record<string, string[]> = {
  groq: [
    "llama-3.3-70b-versatile",
    "openai/gpt-oss-120b",
    "llama-3.1-8b-instant",
  ],
  gemini: ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
  openai: ["gpt-4o", "gpt-4o-mini", "o3-mini"],
  ollama: ["llama3", "mistral", "phi3"],
  tavily: ["tavily-search-v1"],
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
  const {
    credentials,
    saveCredential,
    verifyCredential,
    deleteCredential,
    isSaving: isSavingCred,
  } = useAICredentials();
  const { providers, refetchProviders } = useAIProviders();

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
  const [defaultProvider, setDefaultProvider] = useState("groq");
  const [defaultModel, setDefaultModel] = useState("llama-3.3-70b-versatile");
  const [maxTokens, setMaxTokens] = useState("4096");
  const [temperature, setTemperature] = useState("0.2");

  // BYOK Key Input States
  const [byokProvider, setByokProvider] = useState("groq");
  const [byokApiKey, setByokApiKey] = useState("");
  const [verifyingProvider, setVerifyingProvider] = useState<string | null>(
    null,
  );

  // Theme & Language
  const [theme, setTheme] = useState("Dark");
  const [language, setLanguage] = useState("English");
  const [reducedMotion, setReducedMotion] = useState(false);
  const [highContrast, setHighContrast] = useState(false);
  const [largeText, setLargeText] = useState(false);

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
      await api.patch("/users/me", {
        name: profileName,
        full_name: fullName,
        timezone,
      });
      toast.success("Settings saved successfully");
    } catch (err) {
      toast.error("Failed to save settings");
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveBYOK = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!byokApiKey.trim()) {
      toast.error("Please enter a valid API key.");
      return;
    }
    try {
      await saveCredential({
        provider: byokProvider,
        apiKey: byokApiKey.trim(),
      });
      toast.success(`Saved API key for ${byokProvider.toUpperCase()}`);
      setByokApiKey("");
      refetchProviders();
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || "Failed to save API key");
    }
  };

  const handleVerifyBYOK = async (providerName: string) => {
    setVerifyingProvider(providerName);
    try {
      const res = await verifyCredential(providerName);
      if (res.valid) {
        toast.success(res.message);
      } else {
        toast.error(res.message);
      }
    } catch (err: any) {
      toast.error("Verification failed");
    } finally {
      setVerifyingProvider(null);
    }
  };

  const handleDeleteBYOK = async (providerName: string) => {
    try {
      await deleteCredential(providerName);
      toast.success(`Revoked ${providerName.toUpperCase()} API key`);
      refetchProviders();
    } catch (err: any) {
      toast.error("Failed to revoke API key");
    }
  };

  const sectionCls =
    "p-6 rounded-2xl bg-zinc-950/40 border border-zinc-900 backdrop-blur-xl relative overflow-hidden";
  const sectionHeaderCls =
    "text-base font-semibold text-white mb-4 flex items-center gap-2";
  const labelCls = "text-xs font-medium text-zinc-400 block mb-1.5";
  const inputCls =
    "block w-full px-4 py-2.5 text-xs text-white bg-zinc-900/80 border border-zinc-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all";
  const selectCls =
    "block w-full px-4 py-2.5 text-xs text-white bg-zinc-900/80 border border-zinc-800 rounded-xl focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 outline-none transition-all";

  const renderToggle = (
    label: string,
    desc: string,
    value: boolean,
    onChange: (val: boolean) => void,
  ) => (
    <div className="flex items-center justify-between py-2">
      <div>
        <span className="text-xs font-medium text-white block">{label}</span>
        <span className="text-[11px] text-zinc-500">{desc}</span>
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
          <h1 className="text-3xl font-bold tracking-tight text-white">
            Settings
          </h1>
        </div>
        <p className="text-sm text-zinc-500 leading-relaxed">
          Manage your authenticated profile, AI gateway configurations, and BYOK
          credentials.
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
              <label className={labelCls}>Email Address (Clerk Verified)</label>
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
            Select default AI routing preferences and generation
            hyperparameters.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1.5">
              <label className={labelCls}>Default Provider</label>
              <select
                value={defaultProvider}
                onChange={(e) => {
                  setDefaultProvider(e.target.value);
                  setDefaultModel(
                    MODELS[e.target.value] ? MODELS[e.target.value][0] : "auto",
                  );
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
                {(MODELS[defaultProvider] || ["auto"]).map((m) => (
                  <option key={m} value={m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Save Profile Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isSaving}
            className="flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all cursor-pointer"
          >
            {isSaving ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Save className="w-4 h-4" />
            )}
            Save Profile Settings
          </button>
        </div>
      </form>

      {/* ── BYOK (Bring Your Own Key) Vault Section ── */}
      <div className={sectionCls}>
        <h3 className={sectionHeaderCls}>
          <KeyRound className="w-4 h-4 text-amber-400" />
          AI Provider BYOK Key Vault (Encrypted)
        </h3>
        <p className="text-xs text-zinc-500 mb-5 -mt-2 leading-relaxed">
          Provide your own API keys for personal quota and unthrottled
          capability routing. Keys are encrypted server-side and never exposed.
        </p>

        {/* Active BYOK Credentials Table */}
        {credentials.length > 0 ? (
          <div className="space-y-3 mb-6">
            <span className="text-xs font-medium text-zinc-300">
              Configured BYOK Keys
            </span>
            <div className="space-y-2">
              {credentials.map((c) => (
                <div
                  key={c.id}
                  className="flex items-center justify-between p-3 rounded-xl bg-zinc-900/60 border border-zinc-800/80 text-xs"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-400" />
                    <div>
                      <span className="font-semibold text-white uppercase">
                        {c.provider}
                      </span>
                      <span className="text-zinc-500 ml-2 font-mono">
                        {c.key_hint}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => handleVerifyBYOK(c.provider)}
                      disabled={verifyingProvider === c.provider}
                      className="px-3 py-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 rounded-lg font-medium text-[11px] flex items-center gap-1.5 transition-all"
                    >
                      {verifyingProvider === c.provider ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : (
                        <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                      )}
                      Test Connectivity
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDeleteBYOK(c.provider)}
                      className="p-1.5 text-zinc-500 hover:text-red-400 rounded-lg hover:bg-red-500/10 transition-all"
                      title="Revoke Key"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="p-4 mb-6 rounded-xl bg-zinc-900/30 border border-zinc-800/50 text-xs text-zinc-500 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-zinc-400" />
            No personal BYOK keys configured yet. IdeaGPT will route through
            system-managed tier.
          </div>
        )}

        {/* Add Key Form */}
        <form
          onSubmit={handleSaveBYOK}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-zinc-900"
        >
          <div className="space-y-1.5">
            <label className={labelCls}>Provider</label>
            <select
              value={byokProvider}
              onChange={(e) => setByokProvider(e.target.value)}
              className={selectCls}
            >
              {PROVIDERS.map((p) => (
                <option key={p} value={p}>
                  {p.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1.5 md:col-span-2">
            <label className={labelCls}>API Key</label>
            <div className="flex gap-2">
              <input
                type="password"
                placeholder={`Enter your ${byokProvider.toUpperCase()} API key`}
                value={byokApiKey}
                onChange={(e) => setByokApiKey(e.target.value)}
                className={inputCls}
              />
              <button
                type="submit"
                disabled={isSavingCred || !byokApiKey.trim()}
                className="px-4 py-2 bg-amber-600 hover:bg-amber-500 disabled:opacity-50 text-white rounded-xl text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 cursor-pointer shadow-md shadow-amber-600/20"
              >
                {isSavingCred ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Save className="w-3.5 h-3.5" />
                )}
                Add Key
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* ── System Preferences & Shortcuts ── */}
      <div className={sectionCls}>
        <h3 className={sectionHeaderCls}>
          <Keyboard className="w-4 h-4 text-emerald-400" />
          Global Keyboard Shortcuts
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
          {SHORTCUT_MAP.map((sc) => (
            <div
              key={sc.action}
              className="flex items-center justify-between p-3 rounded-xl bg-zinc-900/40 border border-zinc-900"
            >
              <span className="text-zinc-400">{sc.action}</span>
              <kbd className="px-2 py-1 bg-zinc-800/80 border border-zinc-700/50 rounded-lg text-zinc-300 font-mono text-[10px]">
                {sc.keys}
              </kbd>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
