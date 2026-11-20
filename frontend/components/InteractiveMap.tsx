"use client";

import { MapPoint } from "@/lib/types";
import { useState, useMemo } from "react";
import { MapPin, ZoomIn, ZoomOut, RotateCcw, Layers, Globe } from "lucide-react";

interface InteractiveMapProps {
  points: MapPoint[];
  selectedCity: string;
  onSelectCity: (city: string) => void;
}

export default function InteractiveMap({ points, selectedCity, onSelectCity }: InteractiveMapProps) {
  const [zoom, setZoom] = useState(1);
  const [viewCenter, setViewCenter] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredPoint, setHoveredPoint] = useState<MapPoint | null>(null);
  const [showHeatmap, setShowHeatmap] = useState(true);

  // Convert lat/long to Mercator SVG projection coordinates (width 1000, height 500)
  const projectedPoints = useMemo(() => {
    return points
      .filter((p) => typeof p.lat === "number" && typeof p.lon === "number" && !isNaN(p.lat) && !isNaN(p.lon))
      .map((p) => {
        // Clamp latitude to [-85, 85] to avoid Math.log(0) / Infinity
        const clampedLat = Math.max(-85, Math.min(85, p.lat));
        const x = ((p.lon + 180) * (1000 / 360));
        const latRad = (clampedLat * Math.PI) / 180;
        const mercN = Math.log(Math.tan(Math.PI / 4 + latRad / 2));
        const y = (250 - (1000 * mercN) / (2 * Math.PI));

        // Calculate radius based on job count (min 6, max 32)
        const r = Math.min(Math.max(Math.sqrt(p.job_count) * 2.8, 6), 32);

        return {
          ...p,
          cx: Math.max(10, Math.min(990, x)),
          cy: Math.max(10, Math.min(490, y)),
          r,
        };
      });
  }, [points]);

  const setPreset = (preset: "global" | "india" | "us") => {
    if (preset === "india") {
      setZoom(2.8);
      setViewCenter({ x: -280, y: -80 });
    } else if (preset === "us") {
      setZoom(2.2);
      setViewCenter({ x: 220, y: -40 });
    } else {
      setZoom(1);
      setViewCenter({ x: 0, y: 0 });
    }
  };

  return (
    <div className="relative w-full h-[520px] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 shadow-xl flex flex-col select-none">
      {/* Top Map Control Bar */}
      <div className="absolute top-4 left-4 z-20 flex items-center gap-2">
        <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-xl p-1 flex items-center gap-1 shadow-lg">
          <button
            onClick={() => setPreset("global")}
            className="px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-all"
          >
            🌍 Global
          </button>
          <button
            onClick={() => setPreset("india")}
            className="px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-all"
          >
            🇮🇳 India
          </button>
          <button
            onClick={() => setPreset("us")}
            className="px-2.5 py-1 text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-all"
          >
            🇺🇸 US
          </button>
        </div>

        <button
          onClick={() => setShowHeatmap(!showHeatmap)}
          className={`px-3 py-1.5 text-xs font-semibold rounded-xl border flex items-center gap-1.5 shadow-lg backdrop-blur-md transition-all ${
            showHeatmap
              ? "bg-brand-600/90 border-brand-500 text-white shadow-brand-500/20"
              : "bg-slate-900/90 border-slate-700 text-slate-400 hover:text-white"
          }`}
        >
          <Layers className="w-3.5 h-3.5" />
          Heatmap Overlay
        </button>
      </div>

      {/* Zoom Controls */}
      <div className="absolute top-4 right-4 z-20 flex flex-col gap-1.5">
        <button
          onClick={() => setZoom((z) => Math.min(z + 0.4, 4))}
          className="w-8 h-8 rounded-lg bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700 flex items-center justify-center shadow-lg transition-all"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z - 0.4, 0.8))}
          className="w-8 h-8 rounded-lg bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700 flex items-center justify-center shadow-lg transition-all"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={() => setPreset("global")}
          className="w-8 h-8 rounded-lg bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700 flex items-center justify-center shadow-lg transition-all"
          title="Reset Map"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* SVG Canvas Map */}
      <div className="w-full h-full relative overflow-hidden flex items-center justify-center">
        {projectedPoints.length === 0 ? (
          <div className="text-center text-slate-400 p-8 space-y-2">
            <Globe className="w-10 h-10 mx-auto opacity-30 text-brand-400" />
            <div className="text-sm font-semibold">No coordinate points found</div>
            <div className="text-xs text-slate-500">Try adjusting your filters to see regional clusters</div>
          </div>
        ) : (
          <svg
            viewBox="0 0 1000 500"
            className="w-full h-full transition-transform duration-300 ease-out"
            style={{
              transform: `scale(${zoom}) translate(${viewCenter.x}px, ${viewCenter.y}px)`,
            }}
          >
            <defs>
              <radialGradient id="heatGradient" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#38bdf8" stopOpacity="0.8" />
                <stop offset="40%" stopColor="#3b82f6" stopOpacity="0.5" />
                <stop offset="70%" stopColor="#ef4444" stopOpacity="0.3" />
                <stop offset="100%" stopColor="#ef4444" stopOpacity="0" />
              </radialGradient>
              <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                <feMerge>
                  <feMergeNode in="coloredBlur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            {/* Background Map Grid */}
            <g stroke="#1e293b" strokeWidth="0.5" strokeDasharray="3 3">
              {[100, 200, 300, 400, 500, 600, 700, 800, 900].map((x) => (
                <line key={`x-${x}`} x1={x} y1="0" x2={x} y2="500" />
              ))}
              {[100, 200, 300, 400].map((y) => (
                <line key={`y-${y}`} x1="0" y1={y} x2="1000" y2={y} />
              ))}
            </g>

            {/* Heatmap Glow Circles */}
            {showHeatmap &&
              projectedPoints.map((pt, idx) => (
                <circle
                  key={`heat-${idx}`}
                  cx={pt.cx}
                  cy={pt.cy}
                  r={pt.r * 2.2}
                  fill="url(#heatGradient)"
                  pointerEvents="none"
                />
              ))}

            {/* Interactive Cluster Nodes */}
            {projectedPoints.map((pt, idx) => {
              const isSelected = selectedCity.toLowerCase() === pt.city.toLowerCase();

              return (
                <g
                  key={`node-${idx}`}
                  className="cursor-pointer transition-all duration-200"
                  onClick={() => onSelectCity(pt.city)}
                  onMouseEnter={() => setHoveredPoint(pt)}
                  onMouseLeave={() => setHoveredPoint(null)}
                >
                  {/* Pulse Ring on selection */}
                  {isSelected && (
                    <circle
                      cx={pt.cx}
                      cy={pt.cy}
                      r={pt.r * 1.6}
                      fill="none"
                      stroke="#38bdf8"
                      strokeWidth="2"
                      className="map-pulse"
                    />
                  )}

                  {/* Node Solid Circle */}
                  <circle
                    cx={pt.cx}
                    cy={pt.cy}
                    r={pt.r}
                    fill={isSelected ? "#0284c7" : pt.is_remote ? "#818cf8" : "#f43f5e"}
                    stroke="#ffffff"
                    strokeWidth={isSelected ? 3 : 1.5}
                    filter="url(#glow)"
                    className="hover:scale-125 transition-transform"
                  />

                  {/* Text Label inside circle if big enough */}
                  {pt.r >= 12 && (
                    <text
                      x={pt.cx}
                      y={pt.cy + 3.5}
                      textAnchor="middle"
                      fill="#ffffff"
                      fontSize={pt.r > 16 ? 10 : 8}
                      fontWeight="bold"
                      pointerEvents="none"
                    >
                      {pt.job_count}
                    </text>
                  )}
                </g>
              );
            })}
          </svg>
        )}
      </div>

      {/* Floating Hover Card */}
      {hoveredPoint && (
        <div className="absolute bottom-4 left-4 z-20 bg-slate-900/95 backdrop-blur-md border border-slate-700 p-3 rounded-xl shadow-2xl text-white pointer-events-none animate-in fade-in duration-150">
          <div className="flex items-center gap-1.5 text-xs text-brand-400 font-semibold uppercase tracking-wider">
            <MapPin className="w-3.5 h-3.5" />
            {hoveredPoint.country}
          </div>
          <div className="text-base font-bold mt-0.5">{hoveredPoint.city}</div>
          <div className="text-xs text-slate-300 mt-1 flex items-center gap-2">
            <span className="font-bold text-white bg-brand-600/80 px-2 py-0.5 rounded">
              {hoveredPoint.job_count.toLocaleString()} Active Openings
            </span>
            <span className="text-[11px] text-slate-400">Click to filter</span>
          </div>
        </div>
      )}

      {/* Bottom Map Legend */}
      <div className="absolute bottom-4 right-4 z-20 bg-slate-900/90 backdrop-blur-md border border-slate-700/80 px-3 py-1.5 rounded-xl shadow-lg flex items-center gap-4 text-xs text-slate-300">
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-sm shadow-rose-500"></span>
          <span>Regional Hub</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-400 shadow-sm shadow-indigo-400"></span>
          <span>Remote Base</span>
        </div>
        <div className="text-slate-400 text-[11px]">
          Showing {projectedPoints.length} clusters
        </div>
      </div>
    </div>
  );
}
