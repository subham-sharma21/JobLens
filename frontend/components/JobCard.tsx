"use client";

import { Job } from "@/lib/types";
import { MapPin, Globe, Briefcase, ExternalLink, Building } from "lucide-react";

interface JobCardProps {
  job: Job;
  isSelected?: boolean;
  onSelect: (job: Job) => void;
}

export default function JobCard({ job, isSelected, onSelect }: JobCardProps) {
  return (
    <div
      onClick={() => onSelect(job)}
      className={`group relative p-4 rounded-xl border transition-all cursor-pointer bg-white dark:bg-slate-900 ${
        isSelected
          ? "border-brand-500 ring-2 ring-brand-100 dark:ring-brand-900/50 shadow-md bg-brand-50/20 dark:bg-brand-950/30"
          : "border-slate-200 dark:border-slate-800 hover:border-brand-300 hover:dark:border-brand-500/50 hover:shadow-md"
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          {/* Company Logo / Avatar */}
          <div className="w-10 h-10 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 flex items-center justify-center overflow-hidden shrink-0">
            {job.company_logo ? (
              <img
                src={job.company_logo}
                alt={job.company_name}
                className="w-full h-full object-contain p-1"
                onError={(e) => {
                  (e.target as HTMLElement).style.display = "none";
                }}
              />
            ) : (
              <Building className="w-5 h-5 text-slate-400" />
            )}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-800 dark:text-slate-100 text-sm">{job.company_name}</span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
                {job.ats_type}
              </span>
            </div>
            <div className="text-xs text-slate-500 dark:text-slate-400 font-medium">
              {job.department || job.normalized_role}
            </div>
          </div>
        </div>

        {/* Remote Badge */}
        {job.is_remote ? (
          <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-indigo-700 dark:text-indigo-300 bg-indigo-50 dark:bg-indigo-950/70 border border-indigo-200/60 dark:border-indigo-800/60 px-2 py-0.5 rounded-full shrink-0">
            <Globe className="w-3 h-3" />
            Remote
          </span>
        ) : (
          <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-600 dark:text-slate-300 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full shrink-0">
            <MapPin className="w-3.5 h-3.5 text-slate-500 dark:text-slate-400" />
            On-site
          </span>
        )}
      </div>

      {/* Job Title */}
      <h3 className="mt-2.5 font-bold text-base text-slate-900 dark:text-white group-hover:text-brand-600 group-hover:dark:text-brand-400 transition-colors line-clamp-1">
        {job.title}
      </h3>

      {/* Location & Experience Meta */}
      <div className="mt-2 flex items-center flex-wrap gap-y-1 gap-x-3 text-xs text-slate-500 dark:text-slate-400">
        <div className="flex items-center gap-1">
          <MapPin className="w-3.5 h-3.5 text-slate-400" />
          <span className="truncate max-w-[150px]">{job.city}, {job.country}</span>
        </div>
        {job.experience_min !== null && job.experience_min !== undefined && (
          <div className="flex items-center gap-1 text-slate-600 dark:text-slate-300 font-medium">
            <Briefcase className="w-3.5 h-3.5 text-slate-400" />
            <span>{job.experience_min}{job.experience_max ? `-${job.experience_max}` : "+"} yrs</span>
          </div>
        )}
      </div>

      {/* Skills Chips */}
      {job.skills && job.skills.length > 0 && (
        <div className="mt-3 flex items-center flex-wrap gap-1.5">
          {job.skills.slice(0, 4).map((skill) => (
            <span
              key={skill}
              className="text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 px-2 py-0.5 rounded-md border border-slate-200/50 dark:border-slate-700/60"
            >
              {skill}
            </span>
          ))}
          {job.skills.length > 4 && (
            <span className="text-[10px] text-slate-400 dark:text-slate-500 font-medium">
              +{job.skills.length - 4} more
            </span>
          )}
        </div>
      )}

      {/* Footer hover hint */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-[11px]">
        <span className="text-slate-400 dark:text-slate-500">
          Role: <strong className="text-slate-600 dark:text-slate-300 font-semibold">{job.normalized_role}</strong>
        </span>
        <span className="text-brand-600 dark:text-brand-400 font-semibold flex items-center gap-1 group-hover:translate-x-0.5 transition-transform">
          View Specs <ExternalLink className="w-3 h-3" />
        </span>
      </div>
    </div>
  );
}
