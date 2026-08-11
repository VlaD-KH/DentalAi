"use client";

import React, { useState } from "react";

interface LogEntry {
  timestamp: string;
  agent: string;
  action: str;
  status: "SUCCESS" | "WORKING" | "LOOPBACK";
}

export const AgentSwarmLogger: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([
    { timestamp: "08:32:01", agent: "CAD Specialist", action: "Tooth 46 segmented (FDI). Margin line extracted (99%)", status: "SUCCESS" },
    { timestamp: "08:32:05", agent: "QA Inspector (VLM)", action: "Min thickness: 0.72 mm [OK]. Undercuts: None detected", status: "SUCCESS" },
    { timestamp: "08:32:12", agent: "CAM & Nesting", action: "Toolpath compiled: 42 min. Slot #4 prepped", status: "SUCCESS" },
  ]);

  return (
    <div className="w-full h-full glass-panel rounded-xl p-3 flex flex-col font-mono text-xs border border-slate-800 justify-between">
      {/* Шапка роя агентов */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
        <span className="font-bold text-slate-200 tracking-wider text-xs flex items-center gap-2 font-sans">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          РОЙ AI-АГЕНТОВ (MCP)
        </span>
        <span className="text-[10px] text-slate-500">MCP tool calls in scrollable log</span>
      </div>

      {/* Логи вызовов инструментов MCP */}
      <div className="flex-1 overflow-y-auto my-2 space-y-1.5 pr-1 text-[11px]">
        {logs.map((log, idx) => (
          <div key={idx} className="p-2 rounded bg-slate-950/90 border border-slate-850 flex flex-col gap-0.5">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-cyan-400 font-bold">[Agent: {log.agent}]</span>
              <span className="text-slate-500">{log.timestamp}</span>
            </div>
            <span className="text-slate-300">• {log.action}</span>
          </div>
        ))}
      </div>

      {/* Кнопки неонового ручного вмешательства из ТЗ */}
      <div className="pt-2 border-t border-slate-800/80 flex flex-col gap-1.5">
        <span className="text-[10px] text-slate-500 font-sans font-semibold">Quick Intervention Controls:</span>
        <div className="grid grid-cols-3 gap-1.5 text-[10px] font-sans">
          <button className="py-1.5 px-2 rounded bg-slate-900 border border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-400 transition-all font-medium">
            Подправить границу
          </button>
          <button className="py-1.5 px-2 rounded bg-slate-900 border border-cyan-500/40 text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-400 transition-all font-medium">
            Добавить 0.1 мм окклюзии
          </button>
          <button className="py-1.5 px-2 rounded bg-cyan-500/20 border border-cyan-400 text-cyan-300 hover:bg-cyan-500/40 font-bold transition-all">
            Перенести в CAM
          </button>
        </div>
      </div>
    </div>
  );
};
