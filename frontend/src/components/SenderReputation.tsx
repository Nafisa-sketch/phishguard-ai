import { RadarChart, PolarGrid, PolarAngleAxis, Radar, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface SenderReputationProps {
  data: { axis: string; value: number }[];
  behaviorScore: number;
  behaviorTrend: number[];
}

export default function SenderReputation({ data, behaviorScore, behaviorTrend }: SenderReputationProps) {
  const trendData = behaviorTrend.map((v, i) => ({ i, v }));

  return (
    <div className="glass rounded-2xl p-6 grid grid-cols-2 gap-4">
      <div>
        <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-2">Sender Reputation</div>
        <ResponsiveContainer width="100%" height={150}>
          <RadarChart data={data} outerRadius={55}>
            <PolarGrid stroke="#232B45" />
            <PolarAngleAxis dataKey="axis" tick={{ fontSize: 9, fill: '#5B6478' }} />
            <Radar dataKey="value" stroke="#6C63FF" fill="#6C63FF" fillOpacity={0.35} strokeWidth={1.5} />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <div className="flex flex-col justify-between">
        <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-2">Behavior Score</div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-white">{behaviorScore}</span>
          <span className="text-[12px] text-slate-500">/100</span>
        </div>
        <div className="w-full h-10 mt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trendData}>
              <defs>
                <linearGradient id="behavior-spark" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#6C63FF" stopOpacity={0.4} />
                  <stop offset="100%" stopColor="#6C63FF" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area type="monotone" dataKey="v" stroke="#6C63FF" strokeWidth={1.5} fill="url(#behavior-spark)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="text-[10.5px] text-slate-500 mt-1">Consistent and reliable behavior</div>
      </div>
    </div>
  );
}
