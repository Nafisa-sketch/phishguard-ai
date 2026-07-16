import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, QrCode, ShieldAlert, ShieldCheck, User, Lock, History, ArrowRight, AlertTriangle } from 'lucide-react';
import RiskGauge from '../components/RiskGauge';
import PsychologyPanel from '../components/PsychologyPanel';
import { analyzeEmail } from '../api/client';
import type { AnalyzeResponse } from '../types';

const LEVEL_COLOR: Record<string, string> = {
  HIGH: '#FF4D6D',
  MEDIUM: '#FFB547',
  LOW: '#FFB547',
  MINIMAL: '#00E676',
};

export default function EmailAnalysis() {
  const [emailText, setEmailText] = useState('');
  const [org, setOrg] = useState('');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const DEVICE_CODE_DEMO = `From: it-support@company-verify.com
Subject: Device Verification Required

Your IT department requires device verification for security compliance.

Please go to https://microsoft.com/devicelogin and enter the code: XYZ-789

This is a routine authentication step.`;

  const handleScan = async () => {
    if (!emailText.trim()) {
      setError('Paste an email before running a scan.');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      const result = await analyzeEmail(emailText, org || undefined);
      setData(result);
    } catch {
      setError('Could not reach the analysis backend. Is api.py running on port 5000?');
    } finally {
      setLoading(false);
    }
  };

  const color = data ? LEVEL_COLOR[data.result.threat_level] : '#00E676';

  return (
    <div className="p-8 max-w-6xl">
      <h1 className="text-2xl font-bold text-white tracking-tight">Email Analysis</h1>
      <p className="text-slate-500 text-[13.5px] mt-1 mb-4">
        Paste a full email to scan it for phishing, spear phishing, BEC, QR-code, and device-code (OAuth) threats.
      </p>

      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setEmailText(DEVICE_CODE_DEMO)}
          className="text-[12px] px-3 py-1.5 rounded-lg bg-card-raised border border-primary/30 text-primary hover:bg-primary/10 transition-colors"
        >
          Try Device Code Phishing Demo
        </button>
      </div>

      <div className="glass rounded-2xl p-6 mb-6">
        <div className="grid grid-cols-3 gap-4">
          <textarea
            value={emailText}
            onChange={(e) => setEmailText(e.target.value)}
            placeholder={'From: ceo.company@gmail.com\nSubject: Urgent wire transfer needed\n\nHi Sarah, please wire $5,000 immediately...'}
            className="col-span-2 h-44 bg-card-raised border border-border rounded-xl p-4 text-[13px] font-mono text-slate-300 placeholder:text-slate-600 resize-none focus:outline-none focus:border-primary/50"
          />
          <div className="flex flex-col gap-3">
            <input
              value={org}
              onChange={(e) => setOrg(e.target.value)}
              placeholder="Organization name (optional)"
              className="bg-card-raised border border-border rounded-xl px-4 py-2.5 text-[13px] text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-primary/50"
            />
            <button
              onClick={handleScan}
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-primary to-accent rounded-xl flex items-center justify-center gap-2 text-white font-medium text-[13.5px] hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {loading ? 'Scanning...' : 'Run Scan'} <ArrowRight size={15} />
            </button>
          </div>
        </div>
        {error && (
          <div className="mt-3 text-[12.5px] text-danger flex items-center gap-2">
            <AlertTriangle size={13} /> {error}
          </div>
        )}
      </div>

      <AnimatePresence>
        {data && (
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
            {/* Uploaded email */}
            <div className="glass rounded-2xl p-6 mb-6">
              <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase mb-4">
                <Mail size={13} /> Uploaded Email
              </div>
              <div className="flex items-center gap-3 pb-4 border-b border-border mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center text-white font-semibold">
                  {(data.parsed.sender || '?')[0].toUpperCase()}
                </div>
                <div>
                  <div className="text-[13px] text-slate-300">{data.parsed.sender || 'Unknown sender'}</div>
                  <div className="text-[15px] font-semibold text-white">{data.parsed.subject || '(no subject)'}</div>
                </div>
              </div>
              <div className="text-[13px] text-slate-400 leading-relaxed whitespace-pre-wrap max-h-40 overflow-y-auto">
                {data.parsed.body}
              </div>
            </div>

            {/* QR panel */}
            {data.result.details.qr_signal.qr_detected && (
              <motion.div
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                className="rounded-2xl p-6 mb-6 border border-danger/40 bg-gradient-to-br from-danger/10 to-card"
              >
                <div className="flex items-center gap-2 text-[11px] tracking-wide text-danger uppercase mb-4 font-semibold">
                  <QrCode size={14} /> QR Code Threat Detected · Quishing
                </div>
                <p className="text-[13px] text-slate-200 mb-3">{data.result.details.qr_signal.risk_note}</p>
                {data.result.details.qr_signal.qr_urls?.map((url) => (
                  <div key={url} className="font-mono text-[12px] text-danger bg-bg border border-danger/20 rounded-lg px-3 py-2 mt-1">
                    → {url}
                  </div>
                ))}
              </motion.div>
            )}

            {/* Score + category */}
            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="glass rounded-2xl p-6 flex items-center gap-5 col-span-1">
                <RiskGauge score={data.result.risk_score} level={data.result.threat_level} />
                <div>
                  <div
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10.5px] font-semibold border mb-2"
                    style={{ color, borderColor: color, background: `${color}18` }}
                  >
                    {data.result.threat_level} RISK
                  </div>
                  <div className="text-[13.5px] text-white font-medium">{data.result.attack_type}</div>
                </div>
              </div>

              <div className="glass rounded-2xl p-6 col-span-2">
                <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase mb-3">
                  <ShieldAlert size={13} /> Objects Detected In Scan
                </div>
                <div className="flex flex-wrap gap-2">
                  {data.result.techniques_detected.length ? (
                    data.result.techniques_detected.map((t) => (
                      <span key={t} className="text-[12px] bg-card-raised border border-white/10 rounded-lg px-3 py-1.5 text-slate-200">
                        {t}
                      </span>
                    ))
                  ) : (
                    <span className="text-[13px] text-slate-500">No flagged objects. Clean scan.</span>
                  )}
                </div>
              </div>
            </div>

            {/* Auth + Sender history */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase mb-3">
                  <Lock size={13} /> Authentication Check
                </div>
                <p className="text-[12.5px] text-slate-400">{data.result.details.auth_signal.summary}</p>
              </div>
              <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase mb-3">
                  <History size={13} /> Sender History
                </div>
                <p className="text-[12.5px] text-slate-400 flex items-center gap-2">
                  {data.result.details.sender_history.seen_before ? (
                    <><ShieldCheck size={14} className="text-success" /> Known sender — {data.result.details.sender_history.previous_count} previous email(s).</>
                  ) : (
                    <><User size={14} className="text-warning" /> First time this sender has emailed you.</>
                  )}
                </p>
              </div>
            </div>

            {/* Psychology */}
            <div className="glass rounded-2xl p-6 mb-6">
              <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-4">Psychological Manipulation</div>
              <PsychologyPanel scores={data.psychology} />
            </div>

            {/* Explanation */}
            <div className="glass rounded-2xl p-6 mb-6">
              <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-3">Why This Email Was Flagged</div>
              <p className="text-[13.5px] text-slate-300 leading-relaxed">{data.explanation}</p>
            </div>

            {/* Recommendation */}
            <div
              className="rounded-2xl p-6 border"
              style={{ borderColor: `${color}40`, background: `${color}0F` }}
            >
              <div className="text-[11px] tracking-wide uppercase mb-3" style={{ color }}>Recommended Action</div>
              <p className="text-[13.5px] text-slate-200">
                {data.result.risk_score >= 70
                  ? 'Do not click links or scan QR codes. Verify through another channel before acting.'
                  : data.result.risk_score >= 40
                  ? "Treat with caution. Verify the sender's identity independently."
                  : data.result.risk_score > 0
                  ? 'Minor red flags present. Stay alert.'
                  : 'No major red flags detected in this email.'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
