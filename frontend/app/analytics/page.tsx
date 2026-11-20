"use client";

import { useEffect, useState } from "react";
import { fetchAnalytics, fetchStats } from "@/lib/api";
import { AnalyticsData, Stats } from "@/lib/types";
import { BarChart3, TrendingUp, Building2, MapPin, Code2, Sparkles, Loader2 } from "lucide-react";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchAnalytics(), fetchStats()])
      .then(([analyticsRes, statsRes]) => {
        setData(analyticsRes);
        setStats(statsRes);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="py-32 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 gap-3">
        <Loader2 className="w-8 h-8 animate-spin text-brand-600 dark:text-brand-400" />
        <div className="text-sm font-medium">Aggregating market intelligence data...</div>
      </div>
    );
  }

  const maxCompanyCount = data?.top_companies[0]?.count || 1;
  const maxSkillCount = data?.top_skills[0]?.count || 1;
  const maxRoleCount = data?.top_roles[0]?.count || 1;
  const maxHubCount = data?.top_hubs[0]?.count || 1;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-brand-600 dark:text-brand-400 text-xs font-bold uppercase tracking-wider mb-1">
          <Sparkles className="w-4 h-4" />
          Labor Demand Intelligence
        </div>
        <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
          Tech Labor Market Analytics
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
          Aggregated hiring demand, tech stack frequency index, and geographic concentration computed across{" "}
          <strong className="text-slate-700 dark:text-slate-200">{stats?.total_jobs.toLocaleString()}</strong> active corporate postings.
        </p>
      </div>

      {/* KPI Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Building2 className="w-4 h-4 text-brand-600 dark:text-brand-400" />
            Tracked Companies
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">{stats?.total_companies}</div>
          <div className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">Greenhouse & Lever ATS</div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <TrendingUp className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Indexed Positions
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">{stats?.total_jobs.toLocaleString()}</div>
          <div className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">Direct official listings</div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-amber-500 dark:text-amber-400" />
            Top Tech Hub
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2 truncate">{stats?.top_city}</div>
          <div className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">Highest active volume</div>
        </div>

        <div className="bg-white dark:bg-slate-900 p-5 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm transition-colors">
          <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <Code2 className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            Remote Flexibility
          </div>
          <div className="text-2xl font-black text-slate-900 dark:text-white mt-2">{stats?.remote_percentage}%</div>
          <div className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">{stats?.remote_count.toLocaleString()} remote jobs</div>
        </div>
      </div>

      {/* Grid: Companies Leaderboard & Skills Demand */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Hiring Companies Leaderboard */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 transition-colors">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              Top Hiring Companies
            </h2>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">By Open Headcount</span>
          </div>

          <div className="space-y-3 pt-2">
            {data?.top_companies.map((c, idx) => {
              const pct = (c.count / maxCompanyCount) * 100;
              return (
                <div key={c.slug} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <span className="w-5 text-slate-400 dark:text-slate-500 font-mono text-[11px]">{idx + 1}.</span>
                      {c.name}
                    </span>
                    <span className="text-slate-600 dark:text-slate-400 font-bold">{c.count.toLocaleString()} jobs</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-500 to-indigo-600 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Most Demanded Tech Skills */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 transition-colors">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Code2 className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              In-Demand Tech Skills Index
            </h2>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">Frequency in Job Specs</span>
          </div>

          <div className="space-y-3 pt-2">
            {data?.top_skills.slice(0, 10).map((s, idx) => {
              const pct = (s.count / maxSkillCount) * 100;
              return (
                <div key={s.skill} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <span className="w-5 text-slate-400 dark:text-slate-500 font-mono text-[11px]">{idx + 1}.</span>
                      {s.skill}
                    </span>
                    <span className="text-slate-600 dark:text-slate-400 font-bold">{s.count.toLocaleString()} mentions</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-emerald-500 to-teal-600 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Grid: Geographic Distribution & Role Categories */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Tech Hubs */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 transition-colors">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <MapPin className="w-5 h-5 text-amber-500 dark:text-amber-400" />
              Regional Hiring Concentration
            </h2>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">Excluding 100% Remote</span>
          </div>

          <div className="space-y-3 pt-2">
            {data?.top_hubs.map((hub, idx) => {
              const pct = (hub.count / maxHubCount) * 100;
              return (
                <div key={`${hub.city}-${hub.country}`} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <span className="w-5 text-slate-400 dark:text-slate-500 font-mono text-[11px]">{idx + 1}.</span>
                      {hub.city}, <span className="text-slate-500 dark:text-slate-400 font-normal">{hub.country}</span>
                    </span>
                    <span className="text-slate-600 dark:text-slate-400 font-bold">{hub.count.toLocaleString()} jobs</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-amber-400 to-rose-500 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Roles Distribution */}
        <div className="bg-white dark:bg-slate-900 p-6 rounded-2xl border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 transition-colors">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-brand-600 dark:text-brand-400" />
              Hiring by Technical Specialization
            </h2>
            <span className="text-xs text-slate-400 dark:text-slate-500 font-medium">Domain Breakdown</span>
          </div>

          <div className="space-y-3 pt-2">
            {data?.top_roles.map((r, idx) => {
              const pct = (r.count / maxRoleCount) * 100;
              return (
                <div key={r.role} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-800 dark:text-slate-200 flex items-center gap-2">
                      <span className="w-5 text-slate-400 dark:text-slate-500 font-mono text-[11px]">{idx + 1}.</span>
                      {r.role}
                    </span>
                    <span className="text-slate-600 dark:text-slate-400 font-bold">{r.count.toLocaleString()} jobs</span>
                  </div>
                  <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-indigo-600 rounded-full transition-all duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
