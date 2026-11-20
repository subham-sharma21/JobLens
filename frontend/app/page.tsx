"use client";

import { useEffect, useState, useCallback } from "react";
import FilterSidebar from "@/components/FilterSidebar";
import InteractiveMap from "@/components/InteractiveMap";
import JobCard from "@/components/JobCard";
import JobDetailDrawer from "@/components/JobDetailDrawer";
import { fetchJobs, fetchMapPoints, fetchFilters } from "@/lib/api";
import { Job, MapPoint, FilterOptions } from "@/lib/types";
import { Loader2, AlertCircle, Compass, Layers, RefreshCw } from "lucide-react";

export default function HomePage() {
  const [filters, setFilters] = useState<FilterOptions | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [mapPoints, setMapPoints] = useState<MapPoint[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Active filter states
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRole, setSelectedRole] = useState("All");
  const [selectedCompany, setSelectedCompany] = useState("All");
  const [selectedCity, setSelectedCity] = useState("All");
  const [selectedRegion, setSelectedRegion] = useState("All");
  const [isRemoteOnly, setIsRemoteOnly] = useState(false);
  const [page, setPage] = useState(0);

  // Active selected job for detail drawer
  const [activeJob, setActiveJob] = useState<Job | null>(null);

  // Initial metadata load
  useEffect(() => {
    fetchFilters()
      .then(setFilters)
      .catch((err) => console.error("Could not fetch filter options:", err));
  }, []);

  // Main data loader
  const loadData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params: Record<string, any> = {
        limit: 30,
        offset: page * 30,
      };

      if (searchQuery.trim()) params.q = searchQuery.trim();
      if (selectedRole !== "All") params.role = selectedRole;
      if (selectedCompany !== "All") params.company = selectedCompany;
      if (selectedCity !== "All") params.city = selectedCity;
      if (selectedRegion !== "All") params.region = selectedRegion;
      if (isRemoteOnly) params.is_remote = true;

      const [jobsData, mapData] = await Promise.all([
        fetchJobs(params),
        fetchMapPoints(params),
      ]);

      setJobs(jobsData.jobs);
      setTotalJobs(jobsData.total);
      setMapPoints(mapData);
    } catch (err: any) {
      setError(err.message || "Failed to communicate with JobLens Backend API");
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, selectedRole, selectedCompany, selectedCity, selectedRegion, isRemoteOnly, page]);

  useEffect(() => {
    const timer = setTimeout(() => {
      loadData();
    }, 250);
    return () => clearTimeout(timer);
  }, [loadData]);

  const handleResetFilters = () => {
    setSearchQuery("");
    setSelectedRole("All");
    setSelectedCompany("All");
    setSelectedCity("All");
    setSelectedRegion("All");
    setIsRemoteOnly(false);
    setPage(0);
  };

  const handleCitySelectFromMap = (city: string) => {
    if (selectedCity.toLowerCase() === city.toLowerCase()) {
      setSelectedCity("All");
    } else {
      setSelectedCity(city);
    }
    setPage(0);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      {/* Error Banner */}
      {error && (
        <div className="mb-6 p-4 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 text-rose-800 dark:text-rose-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 shrink-0" />
            <div className="text-sm font-medium">
              Backend not reachable. Ensure FastAPI backend is running on{" "}
              <code className="bg-rose-100 dark:bg-rose-900/60 px-1.5 py-0.5 rounded font-mono text-xs">http://127.0.0.1:8000</code>.
            </div>
          </div>
          <button
            onClick={loadData}
            className="px-3 py-1.5 bg-rose-600 text-white rounded-lg text-xs font-semibold hover:bg-rose-700 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry
          </button>
        </div>
      )}

      {/* Main Split Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Filters & Controls */}
        <div className="lg:col-span-4 space-y-6">
          <FilterSidebar
            filters={filters}
            selectedRole={selectedRole}
            selectedCompany={selectedCompany}
            selectedCity={selectedCity}
            selectedRegion={selectedRegion}
            isRemoteOnly={isRemoteOnly}
            searchQuery={searchQuery}
            onSearchChange={(q) => {
              setSearchQuery(q);
              setPage(0);
            }}
            onRoleChange={(r) => {
              setSelectedRole(r);
              setPage(0);
            }}
            onCompanyChange={(c) => {
              setSelectedCompany(c);
              setPage(0);
            }}
            onCityChange={(city) => {
              setSelectedCity(city);
              setPage(0);
            }}
            onRegionChange={(reg) => {
              setSelectedRegion(reg);
              setPage(0);
            }}
            onRemoteToggle={(rem) => {
              setIsRemoteOnly(rem);
              setPage(0);
            }}
            onReset={handleResetFilters}
            totalResults={totalJobs}
          />
        </div>

        {/* Right Column: Interactive Map & Job Feed */}
        <div className="lg:col-span-8 space-y-6">
          {/* Geospatial Map Container */}
          <div className="relative">
            <InteractiveMap
              points={mapPoints}
              selectedCity={selectedCity}
              onSelectCity={handleCitySelectFromMap}
            />
          </div>

          {/* Active Filter Pill Bar */}
          {(selectedRole !== "All" || selectedCity !== "All" || selectedCompany !== "All" || selectedRegion !== "All" || isRemoteOnly) && (
            <div className="flex items-center gap-2 flex-wrap text-xs bg-white dark:bg-slate-900 p-3 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider text-[10px]">
                Active Filters:
              </span>
              {selectedRegion !== "All" && (
                <span className="bg-brand-50 text-brand-700 dark:bg-brand-950/70 dark:text-brand-300 px-2 py-1 rounded-md font-medium border border-brand-200 dark:border-brand-800">
                  Region: {selectedRegion}
                </span>
              )}
              {selectedRole !== "All" && (
                <span className="bg-brand-50 text-brand-700 dark:bg-brand-950/70 dark:text-brand-300 px-2 py-1 rounded-md font-medium border border-brand-200 dark:border-brand-800">
                  Role: {selectedRole}
                </span>
              )}
              {selectedCompany !== "All" && (
                <span className="bg-brand-50 text-brand-700 dark:bg-brand-950/70 dark:text-brand-300 px-2 py-1 rounded-md font-medium border border-brand-200 dark:border-brand-800">
                  Company: {selectedCompany}
                </span>
              )}
              {selectedCity !== "All" && (
                <span className="bg-brand-50 text-brand-700 dark:bg-brand-950/70 dark:text-brand-300 px-2 py-1 rounded-md font-medium border border-brand-200 dark:border-brand-800">
                  City: {selectedCity}
                </span>
              )}
              {isRemoteOnly && (
                <span className="bg-indigo-50 text-indigo-700 dark:bg-indigo-950/70 dark:text-indigo-300 px-2 py-1 rounded-md font-medium border border-indigo-200 dark:border-indigo-800">
                  100% Remote Only
                </span>
              )}
              <button
                onClick={handleResetFilters}
                className="text-slate-400 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 ml-auto font-medium text-xs underline"
              >
                Clear all
              </button>
            </div>
          )}

          {/* Job Feed Header */}
          <div className="flex items-center justify-between pt-2">
            <div>
              <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight flex items-center gap-2">
                <Compass className="w-5 h-5 text-brand-600 dark:text-brand-400" />
                Live Corporate Openings
              </h2>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Direct postings from official Greenhouse and Lever applicant tracking systems
              </p>
            </div>
            <div className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              Showing {jobs.length} of {totalJobs.toLocaleString()} total
            </div>
          </div>

          {/* Job Cards Grid / Loading / Empty State */}
          {isLoading ? (
            <div className="py-20 flex flex-col items-center justify-center text-slate-400 dark:text-slate-500 gap-3">
              <Loader2 className="w-8 h-8 animate-spin text-brand-600 dark:text-brand-400" />
              <div className="text-sm font-medium">Scanning live ATS feeds...</div>
            </div>
          ) : jobs.length === 0 ? (
            <div className="p-12 text-center rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
              <div className="w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center mx-auto text-slate-400 dark:text-slate-500">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-slate-800 dark:text-slate-200">No matching jobs found</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-sm mx-auto">
                No active openings match your current filter combination. Try clearing your search keyword or selecting "All Markets".
              </p>
              <button
                onClick={handleResetFilters}
                className="px-4 py-2 bg-brand-600 text-white rounded-xl text-xs font-bold hover:bg-brand-700 transition-colors"
              >
                Reset All Filters
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {jobs.map((job) => (
                <JobCard
                  key={`${job.company_slug}-${job.external_id}`}
                  job={job}
                  isSelected={activeJob?.job_id === job.job_id}
                  onSelect={(j) => setActiveJob(j)}
                />
              ))}
            </div>
          )}

          {/* Pagination Controls */}
          {totalJobs > 30 && (
            <div className="pt-4 flex items-center justify-between border-t border-slate-200 dark:border-slate-800 text-xs font-semibold">
              <button
                disabled={page === 0}
                onClick={() => {
                  setPage((p) => Math.max(0, p - 1));
                  window.scrollTo({ top: 500, behavior: "smooth" });
                }}
                className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                Previous Page
              </button>
              <span className="text-slate-500 dark:text-slate-400">
                Page {page + 1} of {Math.ceil(totalJobs / 30)}
              </span>
              <button
                disabled={(page + 1) * 30 >= totalJobs}
                onClick={() => {
                  setPage((p) => p + 1);
                  window.scrollTo({ top: 500, behavior: "smooth" });
                }}
                className="px-4 py-2 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-200 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-800"
              >
                Next Page
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Slide-Over Job Detail Drawer */}
      <JobDetailDrawer job={activeJob} onClose={() => setActiveJob(null)} />
    </div>
  );
}
