import { useEffect, useState } from 'react';
import { Puzzle, CheckCircle2, XCircle, Mail } from 'lucide-react';
import { getIntegrationsStatus } from '../api/client';
import type { IntegrationStatus } from '../api/client';

export default function Integrations() {
  const [status, setStatus] = useState<IntegrationStatus | null>(null);

  useEffect(() => {
    getIntegrationsStatus().then(setStatus).catch(() => {});
  }, []);

  const gmail = status?.gmail;
  const connected = gmail?.status === 'connected';

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex items-center gap-2 mb-1">
        <Puzzle size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">Integrations</h1>
      </div>
      <p className="text-slate-400 text-[13.5px] mb-8">Connected inbox sources.</p>

      <div className="glass rounded-2xl p-6 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-card-raised flex items-center justify-center">
            <Mail size={22} className="text-primary" />
          </div>
          <div>
            <div className="text-[14px] font-medium text-white">Gmail</div>
            <div className="text-[12px] text-slate-500">
              {connected
                ? 'Connected — read-only access to scan your inbox'
                : gmail?.credentials_found
                ? 'Credentials found, but not yet authorized (run scan_inbox.py)'
                : 'Not configured — see README for setup steps'}
            </div>
          </div>
        </div>
        {connected ? (
          <span className="flex items-center gap-1.5 text-[12px] text-success"><CheckCircle2 size={16} /> Connected</span>
        ) : (
          <span className="flex items-center gap-1.5 text-[12px] text-slate-500"><XCircle size={16} /> Not connected</span>
        )}
      </div>

      <div className="glass rounded-2xl p-6 mt-4 opacity-50">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-card-raised flex items-center justify-center">
            <Mail size={22} className="text-slate-500" />
          </div>
          <div>
            <div className="text-[14px] font-medium text-white">Outlook / Microsoft 365</div>
            <div className="text-[12px] text-slate-500">Not built yet — on the roadmap</div>
          </div>
        </div>
      </div>
    </div>
  );
}
