import { motion } from 'framer-motion';

interface RiskGaugeProps {
  score: number;
  level: string;
}

const LEVEL_COLOR: Record<string, string> = {
  HIGH: '#FF4D6D',
  MEDIUM: '#FFB547',
  LOW: '#FFB547',
  MINIMAL: '#00E676',
};

export default function RiskGauge({ score, level }: RiskGaugeProps) {
  const color = LEVEL_COLOR[level] ?? '#00E676';
  const circumference = 2 * Math.PI * 52;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative w-32 h-32 flex items-center justify-center">
      <svg className="absolute -rotate-90" width="128" height="128" viewBox="0 0 128 128">
        <circle cx="64" cy="64" r="52" fill="none" stroke="#232B45" strokeWidth="10" />
        <motion.circle
          cx="64" cy="64" r="52" fill="none" stroke={color} strokeWidth="10" strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: 'easeOut' }}
          style={{ filter: `drop-shadow(0 0 8px ${color}80)` }}
        />
      </svg>
      <div className="text-center">
        <div className="text-3xl font-bold text-white">{score}</div>
        <div className="text-[10px] text-slate-500 tracking-wide">/ 100</div>
      </div>
    </div>
  );
}
