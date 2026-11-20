"use client";

import { useEffect, useState } from "react";
import { fetchCompanies, triggerSync, addCompany } from "@/lib/api";
import { Company } from "@/lib/types";
import { Building2, RefreshCw, Plus, Globe, Loader2, Sparkles, ShieldCheck } from "lucide-react";

export default function TrackerPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // Add Company Modal state
  const [showAddModal, setShowAddModal] = useState(false);
  const [newCompName, setNewCompName] = useState("");
  const [newCompSlug, setNewCompSlug] = useState("");
  const [newCompATS, setNewCompATS] = useState("greenhouse");
  const [newCompRegion, setNewCompRegion] = useState("India");
  const [newCompIndustry, setNewCompIndustry] = useState("Technology");
  const [addError, setAddError] = useState<string | null>(null);
  const [isAdding, setIsAdding] = useState(false);

  const loadCompanies = () => {
    setLoading(true);
    fetchCompanies()
      .then(setCompanies)
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadCompanies();
  }, []);

  const handleSyncAll = async () => {
    setIsSyncing(true);
    setSyncMessage("Triggering async crawler for all ATS boards...");
    try {
      const res = await triggerSync();
      setSyncMessage(res.message);
      setTimeout(() => {
        loadCompanies();
        setIsSyncing(false);
      }, 3000);
    } catch (e: any) {
      setSyncMessage(e.message);
      setIsSyncing(false);
    }
  };

  const handleSyncSingle = async (slug: string) => {
    setSyncMessage(`Syncing ${slug}...`);
    try {
      await triggerSync(slug);
      setSyncMessage(`Sync scheduled for ${slug}!`);
      setTimeout(() => {
        loadCompanies();
        setSyncMessage(null);
      }, 3000);
    } catch (e: any) {
      setSyncMessage(`Error: ${e.message}`);
    }
  };

  const handleAddCompany = async (e: React.FormEvent) => {
    e.preventDefault();
    setAddError(null);
    setIsAdding(true);
    try {
      await addCompany({
        name: newCompName.trim(),
        slug: newCompSlug.trim().toLowerCase(),
        ats: newCompATS,
        region: newCompRegion,
        industry: newCompIndustry,
      });
      setShowAddModal(false);
      setNewCompName("");
      setNewCompSlug("");
      loadCompanies();
      // Auto trigger sync for new company
      handleSyncSingle(newCompSlug.trim().toLowerCase());
    } catch (err: any) {
      setAddError(err.message || "Failed to add company");
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header with Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-brand-600 dark:text-brand-400 text-xs font-bold uppercase tracking-wider mb-1">
            <ShieldCheck className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            Verified Direct Ingestion Network
          </div>
          <h1 className="text-3xl font-black text-slate-900 dark:text-white tracking-tight">
            ATS Tracked Companies Directory
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 max-w-2xl">
            Real-time synchronization engine connecting directly to Greenhouse and Lever career APIs without middleman aggregators.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2.5 rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-700 transition-all flex items-center gap-2 shadow-sm"
          >
            <Plus className="w-4 h-4" />
            Track New Company
          </button>

          <button
            onClick={handleSyncAll}
            disabled={isSyncing}
            className="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold transition-all shadow-md shadow-brand-500/20 flex items-center gap-2 disabled:opacity-60"
          >
            <RefreshCw className={`w-4 h-4 ${isSyncing ? "animate-spin" : ""}`} />
            {isSyncing ? "Syncing Network..." : "Sync All Boards"}
          </button>
        </div>
      </div>

      {/* Sync Notification Banner */}
      {syncMessage && (
        <div className="p-4 rounded-xl bg-brand-50 dark:bg-brand-950/50 border border-brand-200 dark:border-brand-800/80 text-brand-900 dark:text-brand-200 text-xs font-medium flex items-center gap-2 animate-in fade-in">
          <Sparkles className="w-4 h-4 text-brand-600 dark:text-brand-400 shrink-0" />
          <span>{syncMessage}</span>
        </div>
      )}

      {/* Companies Grid */}
      {loading ? (
        <div className="py-24 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-brand-600 dark:text-brand-400" />
          <div className="text-sm font-medium">Fetching active company registry...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {companies.map((c) => (
            <div
              key={c.slug}
              className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-brand-300 hover:dark:border-brand-500/50 hover:shadow-md transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 flex items-center justify-center p-2 shrink-0">
                      {c.logo ? (
                        <img
                          src={c.logo}
                          alt={c.name}
                          className="w-full h-full object-contain"
                          onError={(e) => {
                            (e.target as HTMLElement).style.display = "none";
                          }}
                        />
                      ) : (
                        <Building2 className="w-6 h-6 text-slate-400" />
                      )}
                    </div>
                    <div>
                      <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-1.5">
                        {c.name}
                      </h3>
                      <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                        {c.industry || "Technology"}
                      </div>
                    </div>
                  </div>

                  <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                    {c.ats_type}
                  </span>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <div className="text-slate-400 dark:text-slate-500 font-medium">Active Openings</div>
                    <div className="text-lg font-black text-slate-900 dark:text-white mt-0.5">
                      {c.active_jobs?.toLocaleString() || 0}
                    </div>
                  </div>
                  <div>
                    <div className="text-slate-400 dark:text-slate-500 font-medium">Region</div>
                    <div className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-1 truncate">
                      {c.region || "Global"}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs">
                <div className="text-[11px] text-slate-400 dark:text-slate-500">
                  {c.last_synced_at ? (
                    <span>Synced {new Date(c.last_synced_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  ) : (
                    <span>Pending initial sync</span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  {c.website && (
                    <a
                      href={c.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg transition-colors"
                      title="Visit Company Website"
                    >
                      <Globe className="w-3.5 h-3.5" />
                    </a>
                  )}
                  <button
                    onClick={() => handleSyncSingle(c.slug)}
                    className="px-2.5 py-1 text-[11px] font-semibold text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/60 hover:bg-brand-100 dark:hover:bg-brand-900/60 border border-brand-200 dark:border-brand-800 rounded-lg transition-colors flex items-center gap-1"
                  >
                    <RefreshCw className="w-3 h-3" />
                    Sync
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add Company Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div
            onClick={() => setShowAddModal(false)}
            className="absolute inset-0 bg-slate-900/50 dark:bg-slate-950/80 backdrop-blur-sm"
          />
          <div className="relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-5 animate-in zoom-in-95 duration-200">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">Track New Company Board</h2>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
                Enter any company's official Greenhouse or Lever board slug to ingest its listings.
              </p>
            </div>

            {addError && (
              <div className="p-3 rounded-lg bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-200 text-xs">
                {addError}
              </div>
            )}

            <form onSubmit={handleAddCompany} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Company Name</label>
                <input
                  type="text"
                  required
                  value={newCompName}
                  onChange={(e) => setNewCompName(e.target.value)}
                  placeholder="e.g. Swiggy, Uber, Postman"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">
                  ATS Board Slug
                </label>
                <input
                  type="text"
                  required
                  value={newCompSlug}
                  onChange={(e) => setNewCompSlug(e.target.value)}
                  placeholder="e.g. swiggy, uber, figma"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
                <span className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5 block">
                  Found in board URLs (e.g., boards.greenhouse.io/<strong>slug</strong> or jobs.lever.co/<strong>slug</strong>)
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">ATS Platform</label>
                  <select
                    value={newCompATS}
                    onChange={(e) => setNewCompATS(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium text-slate-900 dark:text-slate-100"
                  >
                    <option value="greenhouse">Greenhouse</option>
                    <option value="lever">Lever</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Region</label>
                  <select
                    value={newCompRegion}
                    onChange={(e) => setNewCompRegion(e.target.value)}
                    className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm font-medium text-slate-900 dark:text-slate-100"
                  >
                    <option value="India">India</option>
                    <option value="Global">Global</option>
                    <option value="Remote">Remote</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 mb-1">Industry</label>
                <input
                  type="text"
                  value={newCompIndustry}
                  onChange={(e) => setNewCompIndustry(e.target.value)}
                  placeholder="e.g. Fintech, E-Commerce, DevTools"
                  className="w-full px-3 py-2 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-900 dark:text-slate-100"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-xs font-bold text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isAdding}
                  className="px-5 py-2 text-xs font-bold text-white bg-brand-600 hover:bg-brand-700 rounded-xl shadow-md disabled:opacity-60"
                >
                  {isAdding ? "Adding..." : "Add & Ingest"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
