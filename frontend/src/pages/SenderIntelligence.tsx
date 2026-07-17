import { useEffect, useState } from 'react';
import { UserSearch } from 'lucide-react';
import { getSenders } from '../api/client';
import type { SenderIntel } from '../api/client';

const riskColor = (score: number) => (score >= 70 ? '#FF4D6D' : score >= 40 ? '#FFB547' : score > 0 ? '#FFB547' : '#00E676');

export default function SenderIntelligence() {
  const [senders, setSenders] = useState<SenderIntel[]>([]);

  useEffect(() => {
    getSenders().then(setSenders).catch(() => {});
  }, []);

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-center gap-2 mb-1">
        <UserSearch size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">Sender Intelligence</h1>
      </div>
      <p className="text-slate-400 text-[13.5px] mb-8">
        Every sender you've received email from, ranked by risk. Built from your own scan history.
      </p>

      <div className="glass rounded-2xl overflow-hidden">
        <table className="w-full text-[12.5px]">
          <thead>
            <tr className="border-b border-border text-slate-500 text-[10.5px] uppercase tracking-wide">
              <th className="text-left px-5 py-3 font-medium">Sender</th>
              <th className="text-right px-5 py-3 font-medium">Emails</th>
              <th className="text-right px-5 py-3 font-medium">Avg Risk</th>
              <th className="text-right px-5 py-3 font-medium">Highest Risk</th>
              <th className="text-right px-5 py-3 font-medium">Last Seen</th>
            </tr>
          </thead>
          <tbody>
            {senders.map((s) => (
              <tr key={s.sender} className="border-b border-border last:border-0 hover:bg-white/[0.02]">
                <td className="px-5 py-3 text-slate-300">{s.sender}</td>
                <td className="px-5 py-3 text-right text-slate-400">{s.email_count}</td>
                <td className="px-5 py-3 text-right font-mono" style={{ color: riskColor(s.avg_risk) }}>{s.avg_risk}</td>
                <td className="px-5 py-3 text-right font-mono" style={{ color: riskColor(s.max_risk) }}>{s.max_risk}</td>
                <td className="px-5 py-3 text-right text-slate-500">{new Date(s.last_seen).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {!senders.length && <div className="text-slate-500 text-[13px] text-center py-10">No senders yet — scan some emails first.</div>}
      </div>
    </div>
  );
}
