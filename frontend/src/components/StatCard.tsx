import { motion } from 'framer-motion';
import type { LucideIcon } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer } from 'recharts';

interface StatCardProps {
  label: string;
  value: string | number;
  suffix?: string;
  icon: LucideIcon;
  accent?: 'primary' | 'success' | 'warning' | 'danger';
  trend?: string;
  sparkData?: number[];
  delay?: number;
}

const ACCENT = {
  primary: { icon: '#6C63FF', bg: 'rgba(108,99,255,0.15)', line: '#6C63FF' },
  success: { icon: '#00E676', bg: 'rgba(0,230,118,0.15)', line: '#00E676' },
  warning: { icon: '#FFB547', bg: 'rgba(255,181,71,0.15)', line: '#FFB547' },
  danger: { icon: '#FF4D6D', bg: 'rgba(255,77,109,0.15)', line: '#FF4D6D' },
};

export default function StatCard({ label, value, suffix, icon: Icon, accent = 'primary', trend, sparkData, delay = 0 }: StatCardProps) {
  const c = ACCENT[accent];
  const chartData = (sparkData ?? [4, 6, 5, 8, 7, 9, 8]).map((v, i) => ({ i, v }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      whileHover={{ y: -3, scale: 1.015 }}
      className="glass rounded-2xl p-5 relative overflow-hidden transition-shadow duration-300"
      style={{ boxShadow: `0 4px 20px ${c.bg}` }}
      onMouseEnter={(e) => (e.currentTarget.style.boxShadow = `0 10px 40px ${c.bg}, 0 0 0 1px ${c.icon}30`)}
      onMouseLeave={(e) => (e.currentTarget.style.boxShadow = `0 4px 20px ${c.bg}`)}
    >
      <div className="absolute top-0 left-0 right-0 h-[2px]" style={{ background: `linear-gradient(90deg, transparent, ${c.icon}, transparent)` }} />
      <div className="flex items-start justify-between">
        <div className="w-11 h-11 rounded-xl flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${c.bg}, transparent)`, boxShadow: `0 0 20px ${c.bg}` }}>
          <Icon size={19} style={{ color: c.icon }} strokeWidth={2} />
        </div>
      </div>
      <div className="mt-4 flex items-baseline gap-1.5">
        <span className="text-[30px] font-extrabold text-white tracking-tight leading-none">{value}</span>
        {suffix && <span className="text-[13px] text-slate-500">{suffix}</span>}
      </div>
      <div className="text-[12px] text-slate-400 mt-1.5">{label}</div>
      <div className="flex items-end justify-between mt-2">
        {trend && <span className="text-[10.5px] font-medium" style={{ color: c.icon }}>{trend}</span>}
        <div className="w-16 h-6 ml-auto opacity-90">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id={`spark-${label}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={c.line} stopOpacity={0.5} />
                  <stop offset="100%" stopColor={c.line} stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="v" stroke={c.line} strokeWidth={1.75} fill={`url(#spark-${label})`} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.div>
  );
}
