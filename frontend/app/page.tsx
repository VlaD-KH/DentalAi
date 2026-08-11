"use client";

import React, { useState } from "react";
import { Viewport3D } from "../components/Viewport3D";
import { AgentSwarmLogger } from "../components/AgentSwarmLogger";

export default function DashboardPage() {
  const [autonomousMode, setAutonomousMode] = useState(true);
  const [activeLang, setActiveLang] = useState<"RU" | "EN" | "PL">("RU");

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 p-4 flex flex-col gap-4 font-sans">
      {/* ===================================================================== */}
      {/* 1. SYSTEM HEALTH BAR & METRICS                                       */}
      {/* ===================================================================== */}
      <header className="w-full bg-slate-900/90 border border-slate-800 rounded-xl p-3 px-5 flex items-center justify-between shadow-lg">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-black text-xl text-white shadow-cyan-500/20 shadow-lg">
            D
          </div>
          <div>
            <h1 className="font-bold text-lg leading-tight tracking-wide text-slate-100">
              DentalAi <span className="text-xs font-normal text-cyan-400">v1.0 Solo-Lab Autonomous OS</span>
            </h1>
            <p className="text-xs text-slate-400">Szczecin, Poland — MDR EU 2017/745 Annex XIII Compliant</p>
          </div>
        </div>

        {/* Индикаторы здоровья системы */}
        <div className="flex items-center gap-6 text-xs">
          <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-emerald-500/50 shadow" />
            <span className="text-slate-300">GPU: NVIDIA L4 (24GB VRAM)</span>
          </div>

          <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800">
            <span className="text-cyan-400 font-mono">FastMCP 3.4.7</span>
            <span className="text-slate-400">Server Online</span>
          </div>

          {/* Переключатель языка i18n */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
            {(["RU", "EN", "PL"] as const).map((lang) => (
              <button
                key={lang}
                onClick={() => setActiveLang(lang)}
                className={`px-2 py-1 rounded font-bold text-[11px] transition-all ${
                  activeLang === lang
                    ? "bg-cyan-500 text-slate-950 shadow"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {lang}
              </button>
            ))}
          </div>

          {/* Переключатель Автономного режима */}
          <button
            onClick={() => setAutonomousMode(!autonomousMode)}
            className={`px-4 py-2 rounded-lg font-semibold border text-xs transition-all flex items-center gap-2 ${
              autonomousMode
                ? "bg-emerald-500/10 border-emerald-500 text-emerald-400 hover:bg-emerald-500/20"
                : "bg-amber-500/10 border-amber-500 text-amber-400 hover:bg-amber-500/20"
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${autonomousMode ? "bg-emerald-400" : "bg-amber-400"}`} />
            {autonomousMode ? "Fully Autonomous Mode" : "Supervised Review Mode"}
          </button>
        </div>
      </header>

      {/* ===================================================================== */}
      {/* 2. MAIN 5-ZONE LAYOUT                                                 */}
      {/* ===================================================================== */}
      <div className="flex-1 grid grid-cols-12 gap-4">
        {/* ЛЕВАЯ КОЛОНКА: Очередь Заказов (3 Колонки) */}
        <section className="col-span-3 bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col gap-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h2 className="font-bold text-sm text-slate-200">B2B Order Queue</h2>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">3 Orders</span>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto pr-1">
            {/* Карточка Заказа #ORD-1042 */}
            <div className="p-3 rounded-lg bg-slate-950 border border-cyan-500/30 hover:border-cyan-500 transition-all cursor-pointer">
              <div className="flex justify-between items-start">
                <span className="font-mono font-bold text-cyan-400">#ORD-1042</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800">
                  COMPLETED
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-1 font-medium">BioDent Clinic (Szczecin)</p>
              <div className="mt-2 text-[11px] text-slate-400 flex justify-between">
                <span>Tooth #46 (FDI)</span>
                <span>Zirconia A2</span>
              </div>
            </div>

            {/* Карточка Заказа #BRIDGE-100 */}
            <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 hover:border-slate-700 transition-all cursor-pointer">
              <div className="flex justify-between items-start">
                <span className="font-mono font-bold text-slate-200">#BRIDGE-100</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-blue-950 text-blue-400 border border-blue-800">
                  CAM NESTING
                </span>
              </div>
              <p className="text-xs text-slate-300 mt-1 font-medium">DentArt Studio</p>
              <div className="mt-2 text-[11px] text-slate-400 flex justify-between">
                <span>Bridge #45-47 (3 units)</span>
                <span>Zirconia Multi</span>
              </div>
            </div>
          </div>
        </section>

        {/* ЦЕНТРАЛЬНАЯ ЗОНА: 3D CAD/CAM Viewport + Agent Swarm Log (6 Колонок) */}
        <section className="col-span-6 flex flex-col gap-4">
          <div className="h-[420px] w-full">
            <Viewport3D />
          </div>

          <div className="h-[220px] w-full">
            <AgentSwarmLogger />
          </div>
        </section>

        {/* ПРАВАЯ КОЛОНКА: Телеметрия ЧПУ & Печи Синтеризации (3 Колонки) */}
        <section className="col-span-3 bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col gap-4">
          <div className="pb-2 border-b border-slate-800">
            <h2 className="font-bold text-sm text-slate-200">Hardware Telemetry</h2>
          </div>

          {/* Телеметрия 5-осевого ЧПУ фрезера */}
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-slate-300">5-Axis CNC Mill</span>
              <span className="text-emerald-400 font-mono">IDLE / READY</span>
            </div>
            <div className="text-[11px] text-slate-400 space-y-1 font-mono">
              <div className="flex justify-between">
                <span>Spindle Speed:</span>
                <span className="text-slate-200">45,000 RPM</span>
              </div>
              <div className="flex justify-between">
                <span>Feed Rate:</span>
                <span className="text-slate-200">1,500 mm/min</span>
              </div>
              <div className="flex justify-between">
                <span>Bur Lifetime:</span>
                <span className="text-emerald-400">92% (Ø0.6mm micro)</span>
              </div>
            </div>
          </div>

          {/* Телеметрия Печи Синтеризации */}
          <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-slate-300">Sintering Furnace</span>
              <span className="text-amber-400 font-mono">HEATING</span>
            </div>
            <div className="text-[11px] text-slate-400 space-y-1 font-mono">
              <div className="flex justify-between">
                <span>Current Temp:</span>
                <span className="text-amber-400 font-bold">1530 °C</span>
              </div>
              <div className="flex justify-between">
                <span>Ramp Rate:</span>
                <span className="text-slate-200">10 °C / min</span>
              </div>
              <div className="flex justify-between">
                <span>Hold Time Remaining:</span>
                <span className="text-slate-200">45 min</span>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
