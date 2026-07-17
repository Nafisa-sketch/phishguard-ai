import { useEffect, useState } from 'react';
import { BookOpen, Clock } from 'lucide-react';
import { getAttackStories } from '../api/client';
import type { ScanRecord } from '../types';

const LEVEL_COLOR: Record<string, string> = {
  HIGH: '#FF4D6D',
  MEDIUM: '#FFB547',
  LOW: '#FFB547',
  MINIMAL: '#00E676',
};

export default function AttackStories() {
  const [stories, setStories] = useState<ScanRecord[]>([]);

  useEffect(() => {
    getAttackStories(60).then(setStories).catch(() => {});
  }, []);

  return (
    <div className="p-8 max-w-4xl">
      <div className="flex items-center gap-2 mb-1">
        <BookOpen size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">Attack Stories</h1>
      </div>
      <p className="text-slate-400 text-[13.5px] mb-8">
        Every high-risk email you've scanned (risk score 60+), told as a plain-language story of what it tried to do.
      </p>

      <div className="space-y-4">
        {stories.map((s) => {
          const color = LEVEL_COLOR[s.threat_level] ?? '#00E676';
          const techniques: string[] = JSON.parse(s.techniques || '[]');
          return (
            <div key={s.id} className="glass rounded-2xl p-6 border" style={{ borderColor: `${color}30` }}>
              <div className="flex items-center justify-between mb-3">
                <span className="text-[15px] font-semibold text-white">{s.attack_type}</span>
                <span className="text-[10.5px] font-semibold px-2.5 py-1 rounded-full border" style={{ color, borderColor: color, background: `${color}18` }}>
                  {s.risk_score}/100
                </span>
              </div>
              <div className="text-[12px] text-slate-500 flex items-center gap-1.5 mb-3">
                <Clock size={12} /> {new Date(s.scanned_at).toLocaleString()} · From {s.sender}
              </div>
              <p className="text-[13.5px] text-slate-300 leading-relaxed mb-3">{s.explanation}</p>
              <div className="flex flex-wrap gap-1.5">
                {techniques.map((t) => (
                  <span key={t} className="text-[10.5px] bg-card-raised border border-white/10 rounded-md px-2 py-1 text-slate-400">{t}</span>
                ))}
              </div>
            </div>
          );
        })}
        {!stories.length && (
          <div className="glass rounded-2xl p-10 text-center text-slate-500 text-[13px]">
            No high-risk emails scanned yet. Try the Device Code Phishing demo in Email Analysis to see one here.
          </div>
        )}
      </div>
    </div>
  );
}
