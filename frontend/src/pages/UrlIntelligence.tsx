import { useState } from 'react';
import { Link2, Search, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { checkUrl } from '../api/client';

export default function UrlIntelligence() {
  const [url, setUrl] = useState('');
  const [result, setResult] = useState<{ url: string; suspicious: boolean; flagged_as: string[] } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleCheck = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await checkUrl(url.trim());
      setResult(res);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-3xl">
      <div className="flex items-center gap-2 mb-1">
        <Link2 size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">URL Intelligence</h1>
      </div>
      <p className="text-slate-400 text-[13.5px] mb-8">
        Paste any link to check for common phishing red flags — disguised IP addresses, excessive subdomains, and other structural warning signs.
      </p>

      <div className="glass rounded-2xl p-5 flex gap-3 mb-6">
        <input
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleCheck()}
          placeholder="https://example.com/login"
          className="flex-1 bg-card-raised border border-border rounded-lg px-4 py-2.5 text-[13px] font-mono text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-primary/50"
        />
        <button
          onClick={handleCheck}
          disabled={loading}
          className="px-5 rounded-lg bg-gradient-to-r from-primary to-accent text-white text-[13px] font-medium flex items-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-50"
        >
          <Search size={14} /> {loading ? 'Checking...' : 'Check'}
        </button>
      </div>

      {result && (
        <div className={`glass rounded-2xl p-6 border ${result.suspicious ? 'border-danger/40' : 'border-success/40'}`}>
          {result.suspicious ? (
            <div className="flex items-start gap-3">
              <AlertTriangle size={20} className="text-danger shrink-0 mt-0.5" />
              <div>
                <div className="text-[14px] font-medium text-white mb-1">Suspicious structure detected</div>
                <p className="text-[12.5px] text-slate-400 mb-3">
                  This link uses a raw IP address or an unusual number of subdomains — a common way attackers disguise a malicious destination.
                </p>
                <div className="font-mono text-[12px] text-danger bg-bg border border-danger/20 rounded-lg px-3 py-2 break-all">{result.url}</div>
              </div>
            </div>
          ) : (
            <div className="flex items-start gap-3">
              <CheckCircle2 size={20} className="text-success shrink-0 mt-0.5" />
              <div>
                <div className="text-[14px] font-medium text-white mb-1">No structural red flags found</div>
                <p className="text-[12.5px] text-slate-400">
                  This doesn't mean the site is guaranteed safe — only that it doesn't match our known suspicious URL patterns.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
