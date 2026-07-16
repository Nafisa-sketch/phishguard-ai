import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

interface ThreatDonutProps {
  data: { name: string; value: number; color: string }[];
  total: number;
}

export default function ThreatDonut({ data, total }: ThreatDonutProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="w-28 h-28 relative shrink-0">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={data} dataKey="value" innerRadius={38} outerRadius={54} paddingAngle={3} strokeWidth={0}>
              {data.map((d) => (
                <Cell key={d.name} fill={d.color} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-lg font-bold text-white">{total}</span>
          <span className="text-[9px] text-slate-500">Total</span>
        </div>
      </div>
      <div className="space-y-1.5 flex-1">
        {data.map((d) => (
          <div key={d.name} className="flex items-center justify-between text-[11px]">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: d.color }} />
              <span className="text-slate-300">{d.name}</span>
            </div>
            <span className="text-slate-500">{d.value}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
