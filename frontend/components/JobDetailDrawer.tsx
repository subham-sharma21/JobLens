"use client";

import { Job } from "@/lib/types";
import { X, ExternalLink, MapPin, Globe, Briefcase, Building2, ShieldCheck } from "lucide-react";
import { useEffect } from "react";

interface JobDetailDrawerProps {
  job: Job | null;
  onClose: () => void;
}

function decodeEntities(str: string): string {
  if (!str) return "";
  let s = str;
  if (s.includes("&lt;") || s.includes("&gt;")) {
    s = s
      .replace(/&lt;/g, "<")
      .replace(/&gt;/g, ">")
      .replace(/&quot;/g, '"')
      .replace(/&#39;/g, "'")
      .replace(/&amp;/g, "&");
  }
  return s;
}

function sanitizeHtml(html: string): string {
  if (!html) return "";
  let clean = decodeEntities(html);
  if (clean.includes("&lt;") || clean.includes("&gt;")) {
    clean = decodeEntities(clean);
  }
  return clean
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "")
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, "")
    .replace(/onload\s*=\s*["'][^"']*["']/gi, "")
    .replace(/onerror\s*=\s*["'][^"']*["']/gi, "");
}

export default function JobDetailDrawer({ job, onClose }: JobDetailDrawerProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!job) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        onClick={onClose}
        className="absolute inset-0 bg-slate-900/50 dark:bg-slate-950/80 backdrop-blur-sm transition-opacity animate-in fade-in"
      />

      {/* Slide-over panel */}
      <div className="fixed inset-y-0 right-0 max-w-2xl w-full bg-white dark:bg-slate-900 dark:border-l dark:border-slate-800 shadow-2xl flex flex-col z-10 animate-in slide-in-from-right duration-300 transition-colors">
        {/* Drawer Header */}
        <div className="p-6 border-b border-slate-200 dark:border-slate-800 flex items-start justify-between bg-slate-50/50 dark:bg-slate-950/50">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 flex items-center justify-center p-1.5 shadow-sm">
              {job.company_logo ? (
                <img src={job.company_logo} alt={job.company_name} className="w-full h-full object-contain" />
              ) : (
                <Building2 className="w-6 h-6 text-slate-400" />
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="font-bold text-lg text-slate-900 dark:text-white">{job.company_name}</h2>
                <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950/70 border border-emerald-200 dark:border-emerald-800/80 px-2 py-0.5 rounded-full">
                  <ShieldCheck className="w-3 h-3" />
                  Verified ATS Source
                </span>
              </div>
              <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                {job.department || job.normalized_role} • Tracked via {job.ats_type.toUpperCase()}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:bg-slate-200/60 dark:hover:bg-slate-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Drawer Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Job Title & Meta */}
          <div>
            <h1 className="text-2xl font-black text-slate-900 dark:text-white tracking-tight leading-snug">
              {job.title}
            </h1>

            <div className="mt-4 grid grid-cols-2 sm:grid-cols-3 gap-3">
              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                <div className="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  Location
                </div>
                <div className="mt-1 text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">
                  {job.city}, {job.country}
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                <div className="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-slate-400" />
                  Workplace
                </div>
                <div className="mt-1 text-sm font-semibold text-slate-800 dark:text-slate-200">
                  {job.is_remote ? "100% Remote" : "On-site / Hybrid"}
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200/60 dark:border-slate-700/60">
                <div className="text-xs text-slate-500 dark:text-slate-400 font-medium flex items-center gap-1.5">
                  <Briefcase className="w-3.5 h-3.5 text-slate-400" />
                  Experience
                </div>
                <div className="mt-1 text-sm font-semibold text-slate-800 dark:text-slate-200">
                  {job.experience_min !== null && job.experience_min !== undefined
                    ? `${job.experience_min}${job.experience_max ? `-${job.experience_max}` : "+"} Years`
                    : "Not specified"}
                </div>
              </div>
            </div>
          </div>

          {/* Extracted Skills Section */}
          {job.skills && job.skills.length > 0 && (
            <div className="p-4 rounded-xl bg-brand-50/50 dark:bg-brand-950/40 border border-brand-100 dark:border-brand-900/60">
              <h3 className="text-xs font-bold text-brand-900 dark:text-brand-300 uppercase tracking-wider mb-2.5">
                Key Technologies & Skills Mentioned
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {job.skills.map((skill) => (
                  <span
                    key={skill}
                    className="text-xs font-semibold bg-white dark:bg-slate-800 text-brand-700 dark:text-brand-300 border border-brand-200/80 dark:border-brand-800/80 px-2.5 py-1 rounded-md shadow-2xs"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Job Description Text / HTML */}
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">
              Role Description & Specifications
            </h3>
            {job.description_html ? (
              <div
                className="job-description text-sm text-slate-700 dark:text-slate-300 leading-relaxed font-normal"
                dangerouslySetInnerHTML={{ __html: sanitizeHtml(job.description_html) }}
              />
            ) : (
              <div className="text-sm text-slate-700 dark:text-slate-300 whitespace-pre-line leading-relaxed">
                {job.description_text}
              </div>
            )}
          </div>
        </div>

        {/* Drawer Sticky Footer with Apply Button */}
        <div className="p-4 bg-white dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between gap-4">
          <div className="text-xs text-slate-500 dark:text-slate-400">
            Source: <strong className="text-slate-800 dark:text-slate-200 font-semibold">{job.company_name} Official Portal</strong>
          </div>
          <a
            href={job.apply_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white font-bold text-sm px-6 py-3 rounded-xl shadow-lg shadow-brand-500/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            Apply on Official Career Site <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>
    </div>
  );
}
