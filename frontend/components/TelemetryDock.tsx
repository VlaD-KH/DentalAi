"use client";

import React from "react";

export const TelemetryDock: React.FC = () => {
  return (
    <div className="w-full glass-panel rounded-xl p-4 border border-slate-800 flex flex-col gap-3">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
        <h3 className="text-xs font-bold tracking-wider text-slate-300 uppercase flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          ТЕЛЕМЕТРИЯ ОБОРУДОВАНИЯ (HARDWARE TELEMETRY & SENSORS)
        </h3>
        <span className="text-[10px] font-mono text-slate-500">Live Sensors IO — 50ms</span>
      </div>

      <div className="grid grid-cols-3 gap-4">
        {/* 1. 5-Axis CNC Mill Radial Gauge */}
        <div className="bg-slate-950/80 rounded-lg p-3 border border-slate-800/80 flex items-center gap-4">
          <div className="relative w-20 h-20 flex items-center justify-center">
            <svg aria-label="Spindle RPM Gauge (45,000 RPM)" role="img" className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-slate-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-cyan-400 transition-all duration-1000"
                strokeDasharray="85, 100"
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-sm font-black font-mono text-cyan-400 leading-none">45,000</span>
              <span className="text-[8px] text-slate-400 font-mono">RPM</span>
            </div>
          </div>
          <div className="flex flex-col text-xs font-mono space-y-0.5">
            <span className="font-bold text-slate-200 font-sans">5-Axis CNC Mill</span>
            <span className="text-[11px] text-slate-400">Шпиндель: 45,000 RPM</span>
            <span className="text-[11px] text-slate-400">Фреза: 0.6mm (Wear: 18%)</span>
            <span className="text-[10px] text-emerald-400 font-bold tracking-wider mt-0.5">[RUNNING]</span>
          </div>
        </div>

        {/* 2. Sintering Furnace Radial Gauge */}
        <div className="bg-slate-950/80 rounded-lg p-3 border border-slate-800/80 flex items-center gap-4">
          <div className="relative w-20 h-20 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-slate-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-amber-500 transition-all duration-1000"
                strokeDasharray="90, 100"
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-sm font-black font-mono text-amber-400 leading-none">1380°C</span>
            </div>
          </div>
          <div className="flex flex-col text-xs font-mono space-y-0.5">
            <span className="font-bold text-slate-200 font-sans">Sintering Furnace</span>
            <span className="text-[11px] text-slate-400">Температурный график</span>
            <span className="text-[11px] text-amber-400 font-bold">1380°C / 1530°C</span>
            <span className="text-[10px] text-slate-400 mt-0.5">До конца: 1ч 40м</span>
          </div>
        </div>

        {/* 3. Pneumatic System Radial Gauge */}
        <div className="bg-slate-950/80 rounded-lg p-3 border border-slate-800/80 flex items-center gap-4">
          <div className="relative w-20 h-20 flex items-center justify-center">
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
              <path
                className="text-slate-800"
                strokeWidth="3.5"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
              <path
                className="text-emerald-400 transition-all duration-1000"
                strokeDasharray="100, 100"
                strokeWidth="3.5"
                strokeLinecap="round"
                stroke="currentColor"
                fill="none"
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
              />
            </svg>
            <div className="absolute flex flex-col items-center justify-center text-center">
              <span className="text-sm font-black font-mono text-emerald-400 leading-none">100</span>
              <span className="text-[8px] text-slate-400 font-mono">Bar</span>
            </div>
          </div>
          <div className="flex flex-col text-xs font-mono space-y-0.5">
            <span className="font-bold text-slate-200 font-sans">Pneumatic System</span>
            <span className="text-[11px] text-slate-400">Давление воздуха: 6.4 Bar <span className="text-emerald-400">[Норма]</span></span>
            <span className="text-[11px] text-slate-400">Вытяжка: 100%</span>
            <span className="text-[10px] text-slate-400 mt-0.5">Склад дисков: 12 шт. в слотах</span>
          </div>
        </div>
      </div>
    </div>
  );
};
