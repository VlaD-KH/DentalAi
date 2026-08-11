"use client";

import React, { useState } from "react";
import Link from "next/link";

export default function WikiPage() {
  const [activeSection, setActiveSection] = useState<"MDR" | "MCP" | "CADCAM">("MDR");

  return (
    <main className="min-h-screen bg-[#0b0f17] text-slate-100 p-6 flex flex-col gap-6 font-sans">
      <header className="glass-panel-glow rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link href="/" className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-xs font-mono text-cyan-400 hover:border-cyan-400 transition-all">
            ← Назад в Дашборд
          </Link>
          <h1 className="text-lg font-bold font-mono text-cyan-400">DentalAi — Official Documentation & Wiki</h1>
        </div>
        <span className="text-xs font-mono text-slate-400">MDR EU 2017/745 Annex XIII Standard</span>
      </header>

      <div className="grid grid-cols-12 gap-6 flex-1">
        {/* Навигация по разделам Wiki */}
        <aside className="col-span-3 glass-panel rounded-xl p-4 flex flex-col gap-2">
          <h2 className="text-xs font-bold font-mono text-slate-400 uppercase tracking-wider mb-2">Разделы Wiki</h2>
          <button
            onClick={() => setActiveSection("MDR")}
            className={`p-3 rounded-lg text-left text-xs font-semibold transition-all border ${
              activeSection === "MDR"
                ? "bg-cyan-500/20 border-cyan-400 text-cyan-300"
                : "bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            ⚖️ MDR EU 2017/745 Compliance
          </button>
          <button
            onClick={() => setActiveSection("MCP")}
            className={`p-3 rounded-lg text-left text-xs font-semibold transition-all border ${
              activeSection === "MCP"
                ? "bg-cyan-500/20 border-cyan-400 text-cyan-300"
                : "bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            📡 FastMCP Agent Swarm Specs
          </button>
          <button
            onClick={() => setActiveSection("CADCAM")}
            className={`p-3 rounded-lg text-left text-xs font-semibold transition-all border ${
              activeSection === "CADCAM"
                ? "bg-cyan-500/20 border-cyan-400 text-cyan-300"
                : "bg-slate-950/60 border-slate-800 text-slate-400 hover:text-slate-200"
            }`}
          >
            📐 3D CAD/CAM Geometry Engine
          </button>
        </aside>

        {/* Содержимое активного раздела */}
        <article className="col-span-9 glass-panel rounded-xl p-6 overflow-y-auto space-y-4 text-slate-300 text-sm leading-relaxed">
          {activeSection === "MDR" && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-cyan-400 font-mono">Соответствие Регламенту MDR EU 2017/745 Annex XIII</h2>
              <p>Производство зубопротезных конструкций в зуботехнических лабораториях на территории Европейского Союза регулируется Регламентом MDR (EU) 2017/745 как индивидуальные медицинские изделия (Custom-Made Devices).</p>
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2">
                <h3 className="font-bold text-slate-200">Ключевые пункты Приложения XIII:</h3>
                <ul className="list-disc list-inside space-y-1 text-xs text-slate-400">
                  <li><strong>Запрет CE-маркировки:</strong> Изделия по индивидуальному заказу НЕ ДОЛЖНЫ иметь маркировку CE.</li>
                  <li><strong>Сквозная прослеживаемость (LOT):</strong> Обязательный привязочный номер партий сырья (Upcera, E.max, PMMA).</li>
                  <li><strong>Сроки хранения:</strong> Документация и 3D STL файлы хранятся не менее 10 лет.</li>
                </ul>
              </div>
            </div>
          )}

          {activeSection === "MCP" && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-cyan-400 font-mono">Спецификация FastMCP Сервера ИИ-Агентов</h2>
              <p>Взаимодействие ИИ-моделей и геометрии осуществляется через FastMCP 3.x сервер на порту 8000.</p>
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 font-mono text-xs">
                <div className="text-cyan-400">✓ 14 Registered MCP Tools (segment, margin, crown, bridge, inlay, veneer, pmma, abutment, model, guide, mdr)</div>
                <div className="text-emerald-400">✓ 3 MCP Resources: dental://scans/[id], dental://crowns/[id], dental://passports/[id]</div>
              </div>
            </div>
          )}

          {activeSection === "CADCAM" && (
            <div className="space-y-4">
              <h2 className="text-xl font-bold text-cyan-400 font-mono">3D CAD/CAM Geometry Engine</h2>
              <p>Математическое ядро обработки полигональных сеток (Mesh Processing).</p>
              <div className="p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs">
                <div>• <strong>Margin Line B-spline:</strong> 36 точек с точностью 99%.</div>
                <div>• <strong>Cement Spacer:</strong> 35 мкм радиальный зазор с отступом уступа 0.8 мм.</div>
                <div>• <strong>CAM Nesting:</strong> Усадка x1.22, 2 литника Ø2.5 мм, 5-осевой G-код ISO 6983.</div>
              </div>
            </div>
          )}
        </article>
      </div>
    </main>
  );
}
