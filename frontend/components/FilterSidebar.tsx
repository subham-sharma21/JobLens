"use client";

import { FilterOptions } from "@/lib/types";
import { Search, RotateCcw, MapPin, Building } from "lucide-react";

interface FilterSidebarProps {
  filters: FilterOptions | null;
  selectedRole: string;
  selectedCompany: string;
  selectedCity: string;
  selectedRegion: string;
  isRemoteOnly: boolean;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onRoleChange: (role: string) => void;
  onCompanyChange: (comp: string) => void;
  onCityChange: (city: string) => void;
  onRegionChange: (region: string) => void;
  onRemoteToggle: (remote: boolean) => void;
  onReset: () => void;
  totalResults: number;
}

export default function FilterSidebar({
  filters,
  selectedRole,
  selectedCompany,
  selectedCity,
  selectedRegion,
  isRemoteOnly,
  searchQuery,
  onSearchChange,
  onRoleChange,
  onCompanyChange,
  onCityChange,
  onRegionChange,
  onRemoteToggle,
  onReset,
  totalResults,
}: FilterSidebarProps) {
  const quickRoles = [
    "All",
    "Software Engineer",
    "Backend Engineer",
    "Frontend Engineer",
    "Full Stack Engineer",
    "Data Scientist",
    "Data Engineer",
    "DevOps & Cloud Engineer",
    "Machine Learning & AI",
  ];

  return (
    <div className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-sm space-y-5 transition-colors duration-200">
      {/* Search Input */}
      <div>
        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
          Search Roles & Skills
        </label>
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="e.g. Python, React, Staff Engineer..."
            className="w-full pl-9 pr-4 py-2.5 bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 transition-all text-slate-900 dark:text-slate-100 placeholder:text-slate-400 dark:placeholder:text-slate-500"
          />
        </div>
      </div>

      {/* Region Presets */}
      <div>
        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
          Target Ecosystem
        </label>
        <div className="grid grid-cols-2 gap-1.5 p-1 bg-slate-100 dark:bg-slate-800/80 rounded-xl">
          {[
            { id: "All", label: "🌐 All Markets" },
            { id: "India", label: "🇮🇳 India Hubs" },
            { id: "Global", label: "🌍 Global Tech" },
            { id: "Remote", label: "💻 100% Remote" },
          ].map((reg) => (
            <button
              key={reg.id}
              onClick={() => onRegionChange(reg.id)}
              className={`py-1.5 px-2 text-xs font-semibold rounded-lg transition-all text-center ${
                selectedRegion === reg.id
                  ? "bg-white dark:bg-slate-700 text-brand-700 dark:text-brand-300 shadow-sm border border-slate-200/60 dark:border-slate-600"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
              }`}
            >
              {reg.label}
            </button>
          ))}
        </div>
      </div>

      {/* Role Category Pills */}
      <div>
        <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
          Role Specialization
        </label>
        <div className="flex flex-wrap gap-1.5">
          {quickRoles.map((role) => (
            <button
              key={role}
              onClick={() => onRoleChange(role)}
              className={`text-xs px-2.5 py-1.5 rounded-lg font-medium transition-all ${
                selectedRole === role
                  ? "bg-brand-600 text-white shadow-sm shadow-brand-500/30"
                  : "bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300"
              }`}
            >
              {role}
            </button>
          ))}
        </div>
      </div>

      {/* Dropdown Filters (Company & City) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-slate-100 dark:border-slate-800">
        <div>
          <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1 flex items-center gap-1">
            <Building className="w-3.5 h-3.5 text-slate-400" />
            Company
          </label>
          <select
            value={selectedCompany}
            onChange={(e) => onCompanyChange(e.target.value)}
            className="w-full py-2 px-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
          >
            <option value="All">All Companies ({filters?.companies.length || 0})</option>
            {filters?.companies.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 dark:text-slate-400 mb-1 flex items-center gap-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            City Hub
          </label>
          <select
            value={selectedCity}
            onChange={(e) => onCityChange(e.target.value)}
            className="w-full py-2 px-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-medium text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-1 focus:ring-brand-500"
          >
            <option value="All">All Cities ({filters?.cities.length || 0})</option>
            {filters?.cities.map((city) => (
              <option key={city} value={city}>
                {city}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Remote Only Toggle & Reset */}
      <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
        <label className="flex items-center gap-2 cursor-pointer select-none">
          <input
            type="checkbox"
            checked={isRemoteOnly}
            onChange={(e) => onRemoteToggle(e.target.checked)}
            className="rounded text-brand-600 focus:ring-brand-500 h-4 w-4 border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800"
          />
          <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">Remote Only</span>
        </label>

        <button
          onClick={onReset}
          className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200 hover:underline"
        >
          <RotateCcw className="w-3 h-3" />
          Reset Filters
        </button>
      </div>

      {/* Filter Stats Counter */}
      <div className="text-xs text-slate-500 dark:text-slate-400 text-center pt-1 font-medium bg-slate-50 dark:bg-slate-800/60 py-2 rounded-lg">
        Showing <strong className="text-brand-600 dark:text-brand-400 font-bold">{totalResults.toLocaleString()}</strong> matched opportunities
      </div>
    </div>
  );
}
