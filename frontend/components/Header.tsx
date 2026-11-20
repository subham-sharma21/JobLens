"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, BarChart3, Building2, MapPin, Globe, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";
import { fetchStats } from "@/lib/api";
import { Stats } from "@/lib/types";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  const pathname = usePathname();
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
  }, []);

  return (
    <header className="sticky top-0 z-40 bg-white/95 dark:bg-slate-900/95 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 transition-colors duration-200">
      {/* Top Ticker Bar */}
      <div className="bg-slate-900 dark:bg-slate-950 text-slate-300 text-xs py-1.5 px-4 hidden md:flex items-center justify-between border-b border-slate-800">
        <div className="flex items-center gap-6 overflow-x-auto">
          <div className="flex items-center gap-1.5 font-medium text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            LIVE ATS FEEDS
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Active Opportunities:</span>
            <span className="font-semibold text-white">{stats ? stats.total_jobs.toLocaleString() : "4,300+"}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="text-slate-400">Companies Monitored:</span>
            <span className="font-semibold text-white">{stats ? stats.total_companies : "19"}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-brand-400" />
            <span className="text-slate-400">Remote Ratio:</span>
            <span className="font-semibold text-white">{stats ? `${stats.remote_percentage}%` : "22%"}</span>
          </div>
          <div className="flex items-center gap-1.5">
            <MapPin className="w-3.5 h-3.5 text-amber-400" />
            <span className="text-slate-400">Lead Tech Hub:</span>
            <span className="font-semibold text-white">{stats ? stats.top_city : "San Francisco"}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 text-slate-400">
          <Sparkles className="w-3.5 h-3.5 text-brand-400" />
          <span>Direct Greenhouse & Lever Ingestion</span>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
            <Compass className="w-6 h-6 animate-spin-slow" />
          </div>
          <div>
            <div className="font-black text-xl tracking-tight text-slate-900 dark:text-white flex items-center gap-1.5">
              Job<span className="text-brand-600 dark:text-brand-400">Lens</span>
              <span className="text-[10px] font-bold uppercase tracking-wider bg-brand-100 text-brand-700 dark:bg-brand-950 dark:text-brand-300 dark:border dark:border-brand-800 px-1.5 py-0.5 rounded">
                2.0
              </span>
            </div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 font-medium -mt-1">
              Geospatial Labor Market Intelligence
            </div>
          </div>
        </Link>

        {/* Navigation Tabs and Theme Switcher */}
        <div className="flex items-center gap-2 sm:gap-3">
          <nav className="flex items-center gap-1 sm:gap-2">
            <Link
              href="/"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all ${
                pathname === "/"
                  ? "bg-brand-50 text-brand-700 shadow-sm border border-brand-200 dark:bg-brand-950/70 dark:text-brand-300 dark:border-brand-800"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800"
              }`}
            >
              <Compass className="w-4 h-4" />
              <span>Explorer & Map</span>
            </Link>

            <Link
              href="/analytics"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all ${
                pathname === "/analytics"
                  ? "bg-brand-50 text-brand-700 shadow-sm border border-brand-200 dark:bg-brand-950/70 dark:text-brand-300 dark:border-brand-800"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Market Analytics</span>
            </Link>

            <Link
              href="/tracker"
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm font-semibold transition-all ${
                pathname === "/tracker"
                  ? "bg-brand-50 text-brand-700 shadow-sm border border-brand-200 dark:bg-brand-950/70 dark:text-brand-300 dark:border-brand-800"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-100 dark:text-slate-300 dark:hover:text-white dark:hover:bg-slate-800"
              }`}
            >
              <Building2 className="w-4 h-4" />
              <span>ATS Tracker</span>
            </Link>
          </nav>

          <div className="w-px h-6 bg-slate-200 dark:bg-slate-800 hidden sm:block" />

          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
