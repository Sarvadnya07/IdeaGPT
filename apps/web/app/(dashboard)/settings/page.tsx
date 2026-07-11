"use client";

import React, { useState } from "react";
import { toast } from "sonner";
import { Settings, Save, Shield, User, BellRing } from "lucide-react";

export default function SettingsPage() {
  const [profileName, setProfileName] = useState("David Chen");
  const [email, setEmail] = useState("david@stealthstartup.co");
  const [receiveAlerts, setReceiveAlerts] = useState(true);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    toast.success("Settings updated successfully!");
  };

  return (
    <div className="space-y-8 py-4 select-none max-w-4xl">
      {/* Title */}
      <div className="space-y-2 border-b border-zinc-900 pb-6">
        <h1 className="text-3xl font-bold tracking-tight text-white">
          Settings
        </h1>
        <p className="text-sm text-zinc-500 leading-relaxed">
          Manage your personal workspace preferences, notification rules, and security profiles.
        </p>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Profile Card */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-5 flex items-center gap-2">
            <User className="w-4.5 h-4.5 text-indigo-400" />
            Profile Credentials
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                Full Name
              </label>
              <input
                type="text"
                value={profileName}
                onChange={(e) => setProfileName(e.target.value)}
                className="block w-full px-4 py-2.5 text-xs text-zinc-300 bg-[#070709] border border-zinc-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 rounded-xl outline-none transition-all font-medium"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full px-4 py-2.5 text-xs text-zinc-300 bg-[#070709] border border-zinc-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/20 rounded-xl outline-none transition-all font-medium"
              />
            </div>
          </div>
        </div>

        {/* Notifications Card */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-5 flex items-center gap-2">
            <BellRing className="w-4.5 h-4.5 text-purple-400" />
            Notifications
          </h3>

          <div className="flex items-center justify-between py-2">
            <div className="space-y-0.5">
              <h4 className="text-xs font-bold text-white">Analysis Reports Alert</h4>
              <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
                Receive instant emails and desktop alerts whenever a new AI analysis finishes.
              </p>
            </div>
            <button
              type="button"
              onClick={() => setReceiveAlerts(!receiveAlerts)}
              className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                receiveAlerts ? "bg-indigo-500" : "bg-zinc-800"
              }`}
            >
              <span
                className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                  receiveAlerts ? "translate-x-4" : "translate-x-0"
                }`}
              ></span>
            </button>
          </div>
        </div>

        {/* Security Card */}
        <div className="bg-[#0b0b0d] border border-zinc-900/60 rounded-2xl p-6 shadow-[0_4px_24px_rgba(0,0,0,0.4)]">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-zinc-900/60 pb-3 mb-4 flex items-center gap-2">
            <Shield className="w-4.5 h-4.5 text-emerald-400" />
            Security Preference
          </h3>
          <p className="text-[10px] text-zinc-500 leading-relaxed font-medium">
            Your credentials are secure. Two-factor authentication (2FA) is automatically enabled on Pro Plan accounts for multi-sig vault integrations.
          </p>
        </div>

        {/* Action button */}
        <div className="flex justify-end pt-2">
          <button
            type="submit"
            className="flex items-center gap-2 px-5 py-2.5 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-500 active:scale-[0.98] rounded-xl transition-all shadow-[0_4px_12px_rgba(79,70,229,0.3)]"
          >
            <Save className="w-3.5 h-3.5" />
            Save Preferences
          </button>
        </div>
      </form>
    </div>
  );
}
