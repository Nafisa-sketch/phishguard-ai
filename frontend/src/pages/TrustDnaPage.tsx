import { useEffect, useState } from 'react';
import { Fingerprint } from 'lucide-react';
import { getStats, getSenders } from '../api/client';
import type { Stats } from '../types';
import type { SenderIntel } from '../api/client';
import TrustDna from '../components/TrustDna';

export default function TrustDnaPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [senders, setSenders] = useState<SenderIntel[]>([]);

  useEffect(() => {
    getStats().then(setStats).catch(() => {});
    getSenders().then(setSenders).catch(() => {});
  }, []);

  const trustedSenders = senders
    .filter((s) => s.max_risk < 20)
    .sort((a, b) => a.avg_risk - b.avg_risk)
    .slice(0, 8)
    .map((s) => ({ name: s.sender.split('<')[0].trim() || s.sender, domain: s.sender, score: Math.round(100 - s.avg_risk), icon: (s.sender[0] || '?').toUpperCase() }));

  const riskySenders = senders.filter((s) => s.max_risk >= 40).sort((a, b) => b.max_risk - a.max_risk);

  return (
    <div className="p-8 max-w-5xl">
      <div className="flex items-center gap-2 mb-1">
        <Fingerprint size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">Trust DNA</h1>
      </div>
      <p className="text-slate-400 text-[13.5px] mb-8">
        A behavioral trust profile built entirely from your own scan history — not a generic reputation score.
      </p>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1">
          <TrustDna score={stats?.trust_score ?? 100} topSenders={trustedSenders.slice(0, 3).length ? trustedSenders.slice(0, 3) : [{ name: 'No data yet', domain: '', score: 0, icon: '—' }]} />
        </div>

        <div className="col-span-2 glass rounded-2xl p-6">
          <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-4">Senders Needing Attention</div>
          {riskySenders.length ? (
            <div className="space-y-2">
              {riskySenders.map((s) => (
                <div key={s.sender} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                  <span className="text-[12.5px] text-slate-300 truncate max-w-[60%]">{s.sender}</span>
                  <span className="text-[12px] font-mono text-danger">Risk: {s.max_risk}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-slate-500 text-[13px] text-center py-8">No risky senders detected yet — good sign.</div>
          )}
        </div>
      </div>
    </div>
  );
}
