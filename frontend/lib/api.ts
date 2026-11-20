import { Stats, FilterOptions, Job, MapPoint, AnalyticsData, Company } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchStats(): Promise<Stats> {
  const res = await fetch(`${API_BASE}/api/v1/stats`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load stats");
  return res.json();
}

export async function fetchFilters(): Promise<FilterOptions> {
  const res = await fetch(`${API_BASE}/api/v1/filters`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load filters");
  return res.json();
}

export async function fetchJobs(params: Record<string, any> = {}): Promise<{ total: number; jobs: Job[] }> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "" && value !== "All") {
      query.set(key, String(value));
    }
  }
  const res = await fetch(`${API_BASE}/api/v1/jobs?${query.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load jobs");
  return res.json();
}

export async function fetchJobDetail(jobId: number): Promise<Job> {
  const res = await fetch(`${API_BASE}/api/v1/jobs/${jobId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load job details");
  return res.json();
}

export async function fetchMapPoints(params: Record<string, any> = {}): Promise<MapPoint[]> {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== "" && value !== "All") {
      query.set(key, String(value));
    }
  }
  const res = await fetch(`${API_BASE}/api/v1/map?${query.toString()}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load map data");
  return res.json();
}

export async function fetchAnalytics(): Promise<AnalyticsData> {
  const res = await fetch(`${API_BASE}/api/v1/analytics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load analytics");
  return res.json();
}

export async function fetchCompanies(): Promise<Company[]> {
  const res = await fetch(`${API_BASE}/api/v1/companies`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load companies");
  return res.json();
}

export async function triggerSync(slug?: string): Promise<{ status: string; message: string }> {
  const url = slug ? `${API_BASE}/api/v1/tracker/sync?slug=${slug}` : `${API_BASE}/api/v1/tracker/sync`;
  const res = await fetch(url, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger sync");
  return res.json();
}

export async function addCompany(companyData: { name: string; slug: string; ats: string; region: string; industry: string }): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/companies`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(companyData),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || "Failed to add company");
  }
  return res.json();
}
