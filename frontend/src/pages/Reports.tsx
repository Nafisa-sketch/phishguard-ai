import { useEffect, useState } from 'react';
import { FileBarChart } from 'lucide-react';
import { getHistory } from '../api/client';
import type { ScanRecord } from '../types';

const LEVEL_COLOR: Record<string, string> = {
  HIGH: '#FF4D6D',
  MEDIUM: '#FFB547',
  LOW: '#FFB547',
  MINIMAL: '#00E676',
};

export default function Reports() {
  const [history, setHistory] = useState<ScanRecord[]>([]);

  useEffect(() => {
    getHistory(500).then(setHistory).catch(() => {});
  }, []);

  return (
    <div className="p-8 max-w-6xl">
      <div className="flex items-center gap-2 mb-1">
        <FileBarChart size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">Reports &amp; Logs</h1>
      </div>
      <p className="text-slate-500 text-[13.5px] mb-8">Full history of every email scanned.</p>

      <div className="glass rounded-2xl overflow-hidden">
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="border-b border-border text-slate-500 text-[10.5px] uppercase tracking-wide">
              <th className="text-left px-5 py-3 font-medium">Scanned At</th>
              <th className="text-left px-5 py-3 font-medium">Sender</th>
              <th className="text-left px-5 py-3 font-medium">Subject</th>
              <th className="text-left px-5 py-3 font-medium">Attack Type</th>
              <th className="text-right px-5 py-3 font-medium">Risk</th>
              <th className="text-right px-5 py-3 font-medium">Level</th>
            </tr>
          </thead>
          <tbody>
            {history.map((h) => {
              const color = LEVEL_COLOR[h.threat_level] ?? '#00E676';
              return (
                <tr key={h.id} className="border-b border-border last:border-0 hover:bg-white/[0.02]">
                  <td className="px-5 py-3 text-slate-500">{new Date(h.scanned_at).toLocaleString()}</td>
                  <td className="px-5 py-3 text-slate-300">{h.sender}</td>
                  <td className="px-5 py-3 text-slate-300 max-w-[220px] truncate">{h.subject}</td>
                  <td className="px-5 py-3 text-slate-400">{h.attack_type}</td>
                  <td className="px-5 py-3 text-right font-mono" style={{ color }}>{h.risk_score}</td>
                  <td className="px-5 py-3 text-right">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border" style={{ color, borderColor: color, background: `${color}18` }}>
                      {h.threat_level}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        {!history.length && <div className="text-slate-600 text-[13px] text-center py-10">No scans yet.</div>}
      </div>
    </div>
  );
}
