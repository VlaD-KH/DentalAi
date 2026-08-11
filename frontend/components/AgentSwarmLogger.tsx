"use client";

import React, { useEffect, useState } from "react";

interface LogEntry {
  timestamp: string;
  agent: string;
  action: string;
  status: "SUCCESS" | "WORKING" | "LOOPBACK";
}

export const AgentSwarmLogger: React.FC = () => {
  const [logs, setLogs] = useState<LogEntry[]>([
    { timestamp: "08:32:01", agent: "ToothSegmenter", action: "3D Mesh segmentation for FDI #46 completed", status: "SUCCESS" },
    { timestamp: "08:32:05", agent: "MarginDetector", action: "Margin line B-spline 36 points extracted (Acc: 0.99)", status: "SUCCESS" },
    { timestamp: "08:32:12", agent: "CrownGenerator", action: "Diffusion anatomy generation (Thickness: 0.76mm)", status: "SUCCESS" },
    { timestamp: "08:32:18", agent: "GeometryProcessor", action: "Cement spacer 35um & Occlusion carving -0.05mm applied", status: "SUCCESS" },
    { timestamp: "08:32:24", agent: "QaInspector", action: "VLM Undercut ray-tracing test PASSED", status: "SUCCESS" },
    { timestamp: "08:32:30", agent: "CamEngine", action: "5-Axis G-code compiled (ISO 6983) - Disk Slot #4", status: "SUCCESS" },
    { timestamp: "08:32:35", agent: "MdrPassportGenerator", action: "MDR EU 2017/745 Annex XIII Statement PDF generated", status: "SUCCESS" },
  ]);

  return (
    <div className="w-full h-full bg-slate-900 border border-slate-700 rounded-xl p-4 flex flex-col font-mono text-xs overflow-hidden">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <span className="font-bold text-slate-200 flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          FastMCP Agent Swarm Live Log
        </span>
        <span className="text-slate-500">Port 8000 (Active)</span>
      </div>

      <div className="flex-1 overflow-y-auto mt-3 space-y-2 pr-1">
        {logs.map((log, idx) => (
          <div key={idx} className="flex items-start gap-2 p-2 rounded bg-slate-950/60 border border-slate-850">
            <span className="text-slate-500">{log.timestamp}</span>
            <span className="text-cyan-400 font-semibold">[{log.agent}]</span>
            <span className="text-slate-300 flex-1">{log.action}</span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">
              {log.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
