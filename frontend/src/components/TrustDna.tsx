import { motion } from 'framer-motion';
import { ShieldCheck } from 'lucide-react';

interface TrustDnaProps {
  score: number;
  topSenders: { name: string; domain: string; score: number; icon: string }[];
}

export default function TrustDna({ score, topSenders }: TrustDnaProps) {
  const circumference = 2 * Math.PI * 44;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-1">
        <ShieldCheck size={14} className="text-success" />
        <span className="text-[13px] font-medium text-white">Trust DNA</span>
      </div>
      <div className="text-[11px] text-slate-500 mb-4">All Systems Operational</div>

      <div className="flex flex-col items-center mb-5">
        <div className="relative w-24 h-24">
          <svg className="-rotate-90" width="96" height="96" viewBox="0 0 96 96">
            <circle cx="48" cy="48" r="44" fill="none" stroke="#1E2740" strokeWidth="7" />
            <motion.circle
              cx="48" cy="48" r="44" fill="none" stroke="#00E676" strokeWidth="7" strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 1, ease: 'easeOut' }}
              style={{ filter: 'drop-shadow(0 0 6px #00E67680)' }}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center text-xl font-bold text-white">{score}%</div>
        </div>
        <div className="text-[11px] text-success mt-2">Trusted</div>
      </div>

      <div className="text-[10px] text-slate-500 uppercase tracking-wide mb-2">Top Trusted Senders</div>
      <div className="space-y-2">
        {topSenders.map((s) => (
          <div key={s.domain} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-card-raised flex items-center justify-center text-[10px] text-slate-300">{s.icon}</div>
              <div>
                <div className="text-[11.5px] text-slate-200 leading-tight">{s.name}</div>
                <div className="text-[9.5px] text-slate-600">{s.domain}</div>
              </div>
            </div>
            <span className="text-[11px] text-success">{s.score}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
