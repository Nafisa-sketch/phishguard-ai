import { Construction } from 'lucide-react';

export default function ComingSoon({ title }: { title: string }) {
  return (
    <div className="p-8 h-[70vh] flex flex-col items-center justify-center text-center">
      <div className="w-14 h-14 rounded-2xl bg-card-raised flex items-center justify-center mb-4">
        <Construction size={22} className="text-slate-500" />
      </div>
      <h2 className="text-lg font-semibold text-white mb-1">{title}</h2>
      <p className="text-slate-500 text-[13px] max-w-sm">
        This section is on the roadmap but not built yet — Mission Control, Email Analysis,
        QR Shield, and Reports are fully working.
      </p>
    </div>
  );
}
