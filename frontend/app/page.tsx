"use client";

import React, { useState } from "react";
import { Viewport3D } from "../components/Viewport3D";
import { AgentSwarmLogger } from "../components/AgentSwarmLogger";
import { TelemetryDock } from "../components/TelemetryDock";

export default function DashboardPage() {
  const [autonomousMode, setAutonomousMode] = useState(true);
  const [activeLang, setActiveLang] = useState<"RU" | "EN" | "PL">("RU");

  return (
    <main className="min-h-screen bg-[#0b0f17] text-slate-100 p-3 flex flex-col gap-3 font-sans overflow-x-hidden">
      {/* ===================================================================== */}
      {/* 1. TOP CONTROL & SYSTEM BAR                                           */}
      {/* ===================================================================== */}
      <header className="w-full glass-panel-glow rounded-xl p-2.5 px-4 flex items-center justify-between shadow-xl">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-400 to-emerald-400 flex items-center justify-center font-black text-lg text-slate-950 shadow-cyan-500/50 shadow-md">
            🦷
          </div>
          <div>
            <h1 className="font-extrabold text-sm tracking-wide text-slate-100 flex items-center gap-2 font-mono">
              Dental Autonomous Solo Lab OS
              <span className="text-[10px] font-normal px-2 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-800">
                Single Pane of Glass
              </span>
            </h1>
            <p className="text-[10px] text-slate-400">
              Futuristic yet pragmatic dental CAD/CAM solo laboratory software dashboard
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-mono">
          <div className="flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800 text-[11px]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-slate-300">GPU: NVIDIA L4 (24GB VRAM)</span>
          </div>

          {/* i18n Языковой переключатель */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
            {(["RU", "EN", "PL"] as const).map((lang) => (
              <button
                key={lang}
                onClick={() => setActiveLang(lang)}
                className={`px-2 py-0.5 rounded font-bold text-[10px] transition-all ${
                  activeLang === lang
                    ? "bg-cyan-400 text-slate-950 shadow-md"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {lang}
              </button>
            ))}
          </div>

          {/* Кнопка Режима Автономии */}
          <button
            onClick={() => setAutonomousMode(!autonomousMode)}
            className={`px-3 py-1.5 rounded-lg font-bold border text-[11px] transition-all flex items-center gap-2 font-sans ${
              autonomousMode
                ? "bg-emerald-500/20 border-emerald-400 text-emerald-300 shadow-emerald-500/20 shadow-md"
                : "bg-amber-500/20 border-amber-400 text-amber-300 shadow-amber-500/20 shadow-md"
            }`}
          >
            <span className={`w-2 h-2 rounded-full ${autonomousMode ? "bg-emerald-400" : "bg-amber-400"}`} />
            {autonomousMode ? "Fully Autonomous Mode" : "Supervised Review Mode"}
          </button>
        </div>
      </header>

      {/* ===================================================================== */}
      {/* 2. CENTRAL 3-COLUMN DASHBOARD GRID                                    */}
      {/* ===================================================================== */}
      <div className="grid grid-cols-12 gap-3 flex-1">
        {/* ЛЕВАЯ ПАНЕЛЬ: Очердь Заказов (B2B) - 3 Колоноки */}
        <section className="col-span-3 glass-panel rounded-xl p-3 flex flex-col gap-2.5">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h2 className="font-bold text-xs text-slate-200 tracking-wider font-sans uppercase">
              ОЧЕРЕДЬ ЗАКАЗОВ (B2B)
            </h2>
            <span className="text-[10px] font-mono text-cyan-400 font-bold">Real-time active dental orders</span>
          </div>

          <div className="flex-1 space-y-2.5 overflow-y-auto pr-1">
            {/* Заказ 1: DentArt Зуб 46 */}
            <div className="p-3 rounded-lg bg-slate-950/90 border border-amber-500/40 hover:border-amber-400 transition-all space-y-1.5 shadow-lg">
              <div className="flex justify-between items-start text-xs font-mono">
                <span className="font-bold text-cyan-400">#1042 DentArt: Зуб 46</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-700 font-bold">
                  [В РАБОТЕ]
                </span>
              </div>
              <p className="text-[11px] text-slate-300 font-sans">Сдача: 14:00 (Zirconia)</p>
              
              <button className="w-full py-1 text-[10px] font-sans font-bold bg-slate-900 border border-slate-700 text-slate-300 rounded hover:border-cyan-400 hover:text-cyan-400 transition-all">
                Генерация PDF MDR Паспорта
              </button>

              <div className="flex items-center justify-between text-[10px] pt-1 border-t border-slate-900 font-mono text-slate-400">
                <span>MDR Compliance Badges</span>
                <span className="text-emerald-400">✓ LOT Binding</span>
              </div>
            </div>

            {/* Заказ 2: BioDent Мост 24-26 */}
            <div className="p-3 rounded-lg bg-slate-950/90 border border-cyan-500/40 hover:border-cyan-400 transition-all space-y-1.5 shadow-lg">
              <div className="flex justify-between items-start text-xs font-mono">
                <span className="font-bold text-cyan-400">#1043 BioDent: Мост 24-26</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-400 border border-cyan-700 font-bold">
                  [AI МОДЕЛИРУЕТ]
                </span>
              </div>
              <p className="text-[11px] text-slate-300 font-sans">Сдача: 16:30 (3 units)</p>

              <button className="w-full py-1 text-[10px] font-sans font-bold bg-slate-900 border border-slate-700 text-slate-300 rounded hover:border-cyan-400 hover:text-cyan-400 transition-all">
                Генерация PDF MDR Паспорта
              </button>

              <div className="flex items-center justify-between text-[10px] pt-1 border-t border-slate-900 font-mono text-slate-400">
                <span>MDR Compliance Badges</span>
                <span className="text-emerald-400">✓ LOT Binding</span>
              </div>
            </div>
          </div>
        </section>

        {/* ЦЕНТРАЛЬНАЯ ПАНЕЛЬ: 3D Viewport - 6 Колонок */}
        <section className="col-span-6 h-[440px]">
          <Viewport3D />
        </section>

        {/* ПРАВАЯ ПАНЕЛЬ: Рой AI-Агентов MCP - 3 Колонки */}
        <section className="col-span-3 h-[440px]">
          <AgentSwarmLogger />
        </section>
      </div>

      {/* ===================================================================== */}
      {/* 3. BOTTOM TELEMETRY DOCK                                              */}
      {/* ===================================================================== */}
      <footer className="w-full">
        <TelemetryDock />
      </footer>
    </main>
  );
}
