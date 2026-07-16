import { motion } from 'framer-motion';
import { Zap, Crown, Skull, Coins, Sparkle } from 'lucide-react';

interface PsychologyPanelProps {
  scores: { urgency: number; authority: number; fear: number; greed: number; curiosity: number };
}

const LEVERS = [
  { key: 'urgency', label: 'Urgency', icon: Zap, color: '#FF4D6D' },
  { key: 'authority', label: 'Authority', icon: Crown, color: '#6C63FF' },
  { key: 'fear', label: 'Fear', icon: Skull, color: '#FFB547' },
  { key: 'greed', label: 'Greed', icon: Coins, color: '#00E676' },
  { key: 'curiosity', label: 'Curiosity', icon: Sparkle, color: '#00D9FF' },
] as const;

export default function PsychologyPanel({ scores }: PsychologyPanelProps) {
  return (
    <div className="grid grid-cols-5 gap-3">
      {LEVERS.map((lever, i) => {
        const value = scores[lever.key as keyof typeof scores] ?? 0;
        const Icon = lever.icon;
        return (
          <motion.div
            key={lever.key}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: i * 0.05 }}
            className="glass rounded-xl p-4 flex flex-col items-center text-center"
          >
            <div
              className="w-11 h-11 rounded-full flex items-center justify-center mb-2 relative"
              style={{ background: `${lever.color}18` }}
            >
              <svg className="absolute inset-0 -rotate-90" viewBox="0 0 44 44">
                <circle cx="22" cy="22" r="19" fill="none" stroke={`${lever.color}20`} strokeWidth="3" />
                <circle
                  cx="22" cy="22" r="19" fill="none" stroke={lever.color} strokeWidth="3"
                  strokeDasharray={`${(value / 100) * 119.4} 119.4`}
                  strokeLinecap="round"
                />
              </svg>
              <Icon size={16} style={{ color: lever.color }} />
            </div>
            <div className="text-[11px] text-slate-400">{lever.label}</div>
            <div className="text-[13px] font-semibold text-white mt-0.5">{value}%</div>
          </motion.div>
        );
      })}
    </div>
  );
}
