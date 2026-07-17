import { useEffect, useState } from 'react';
import { Radar, ExternalLink } from 'lucide-react';
import { getThreatFeed } from '../api/client';
import type { ThreatFeedItem } from '../api/client';

export default function ThreatIntelligence() {
  const [threats, setThreats] = useState<ThreatFeedItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getThreatFeed(15).then((data) => {
      setThreats(data);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-center gap-2 mb-1">
        <Radar size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">Threat Intelligence</h1>
      </div>
      <p className="text-slate-400 text-[13.5px] mb-2">
        Live feed of recently reported malicious URLs from URLhaus (abuse.ch) — a free, global threat-intelligence source.
      </p>
      <p className="text-slate-600 text-[11.5px] mb-8">
        Note: this is a global security-research feed, not specific to your own inbox — it shows what a real threat-intel integration looks like.
      </p>

      <div className="glass rounded-2xl overflow-hidden">
        {loading ? (
          <div className="text-slate-500 text-[13px] text-center py-10">Loading live feed...</div>
        ) : threats.length ? (
          <table className="w-full text-[12px]">
            <thead>
              <tr className="border-b border-border text-slate-500 text-[10px] uppercase tracking-wide">
                <th className="text-left px-5 py-3 font-medium">Reported</th>
                <th className="text-left px-5 py-3 font-medium">URL</th>
                <th className="text-left px-5 py-3 font-medium">Threat Type</th>
              </tr>
            </thead>
            <tbody>
              {threats.map((t, i) => (
                <tr key={i} className="border-b border-border last:border-0 hover:bg-white/[0.02]">
                  <td className="px-5 py-3 text-slate-500 whitespace-nowrap">{t.date_added}</td>
                  <td className="px-5 py-3 text-slate-300 font-mono max-w-[380px] truncate">{t.url}</td>
                  <td className="px-5 py-3">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full border border-danger text-danger bg-danger/10">
                      {t.threat_type}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="text-slate-500 text-[13px] text-center py-10 px-6 flex flex-col items-center gap-2">
            <span>Couldn't reach the live feed right now (needs internet access on this machine).</span>
            <a href="https://urlhaus.abuse.ch/browse/" target="_blank" rel="noreferrer" className="text-primary flex items-center gap-1 text-[12px]">
              View feed directly on URLhaus <ExternalLink size={11} />
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
