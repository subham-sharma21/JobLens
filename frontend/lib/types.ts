export interface Job {
  job_id: number;
  external_id: string;
  company_name: string;
  company_slug: string;
  company_logo?: string;
  ats_type: string;
  title: string;
  normalized_role: string;
  department?: string;
  city: string;
  state?: string;
  country: string;
  raw_location: string;
  is_remote: boolean;
  latitude?: number;
  longitude?: number;
  experience_min?: number;
  experience_max?: number;
  salary_min?: number;
  salary_max?: number;
  skills: string[];
  apply_url: string;
  description_text: string;
  description_html: string;
  posted_date?: string;
  source: string;
  created_at?: string;
}

export interface Company {
  id: number;
  name: string;
  slug: string;
  ats_type: string;
  region: string;
  industry: string;
  website: string;
  logo: string;
  active_jobs: number;
  status: string;
  last_synced_at?: string;
  error_message?: string;
}

export interface Stats {
  total_jobs: number;
  total_companies: number;
  total_cities: number;
  remote_count: number;
  remote_percentage: number;
  top_city: string;
  top_role: string;
}

export interface MapPoint {
  city: string;
  country: string;
  lat: number;
  lon: number;
  is_remote: boolean;
  job_count: number;
}

export interface AnalyticsData {
  top_companies: { name: string; slug: string; count: number }[];
  top_roles: { role: string; count: number }[];
  top_hubs: { city: string; country: string; count: number }[];
  top_skills: { skill: string; count: number }[];
}

export interface FilterOptions {
  roles: string[];
  companies: { name: string; slug: string; region: string; logo: string }[];
  cities: string[];
  regions: string[];
}
