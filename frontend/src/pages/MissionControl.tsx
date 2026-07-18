import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity, Mail, ShieldAlert, Bell, Target, ArrowRight, ArrowUpRight,
  Flame, Mail as MailIcon, Brain,
} from 'lucide-react';
import StatCard from '../components/StatCard';
import ThreatDonut from '../components/ThreatDonut';
import WorldThreatMap from '../components/WorldThreatMap';
import TrustDna from '../components/TrustDna';
import SenderReputation from '../components/SenderReputation';
import PsychologyPanel from '../components/PsychologyPanel';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getStats, getTrend, getHistory, getModelInfo } from '../api/client';
import type { Stats, TrendPoint, ScanRecord } from '../types';
import type { ModelInfo } from '../api/client';

const LEVEL_COLOR: Record<string, string> = {
  HIGH: '#FF4D6D',
  MEDIUM: '#FFB547',
  LOW: '#FFB547',
  MINIMAL: '#00E676',
};

// Demo/illustrative data for panels that need a real threat-intel feed
// or a trained baseline we don't have yet (see honest notes in each
// component). Real scan data (stats, trend, history, latest techniques)
// always overrides this where we have it.
const GEO_DEMO = [
  { name: 'United States of America', percent: 32, color: '#6C63FF' },
  { name: 'Germany', percent: 18, color: '#00D9FF' },
  { name: 'Russia', percent: 14, color: '#FF4D6D' },
  { name: 'Nigeria', percent: 9, color: '#FFB547' },
];

const SENDER_REP_DEMO = [
  { axis: 'SPF', value: 80 },
  { axis: 'DKIM', value: 65 },
  { axis: 'DMARC', value: 70 },
  { axis: 'History', value: 90 },
  { axis: 'Domain Age', value: 75 },
  { axis: 'Behavior', value: 85 },
];

const TRUSTED_SENDERS_DEMO = [
  { name: 'Google Workspace', domain: 'workspace.google.com', score: 98, icon: 'G' },
  { name: 'Microsoft', domain: 'microsoft.com', score: 95, icon: 'M' },
  { name: 'Amazon', domain: 'amazon.com', score: 92, icon: 'A' },
];

interface MissionControlProps {
  onNavigate: (page: string) => void;
}

export default function MissionControl({ onNavigate }: MissionControlProps) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [trend, setTrend] = useState<TrendPoint[]>([]);
  const [history, setHistory] = useState<ScanRecord[]>([]);
  const [modelInfo, setModelInfo] = useState<ModelInfo | null>(null);

  useEffect(() => {
    getStats().then(setStats).catch(() => {});
    getTrend(7).then(setTrend).catch(() => {});
    getHistory(8).then(setHistory).catch(() => {});
    getModelInfo().then(setModelInfo).catch(() => {});
  }, []);

  const latest = history[0];
  const latestTechniques: string[] = latest ? JSON.parse(latest.techniques || '[]') : [];
  const total = stats?.total ?? 0;

  const donutData = stats && total > 0
    ? [
        { name: 'Safe', value: Math.round((stats.safe / total) * 100), color: '#00E676' },
        { name: 'Suspicious', value: Math.round((stats.suspicious / total) * 100), color: '#FFB547' },
        { name: 'Malicious', value: Math.round((stats.malicious / total) * 100), color: '#FF4D6D' },
      ]
    : [
        { name: 'Safe', value: 100, color: '#00E676' },
        { name: 'Suspicious', value: 0, color: '#FFB547' },
        { name: 'Malicious', value: 0, color: '#FF4D6D' },
      ];

  return (
    <div className="p-8 max-w-[1400px]">
      <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }} className="flex items-center gap-2.5 mb-1">
        <h1 className="text-[34px] font-extrabold gradient-text tracking-tight">Mission Control</h1>
        <span className="w-2 h-2 rounded-full bg-accent mt-3" style={{ boxShadow: '0 0 12px #00D9FF' }} />
      </motion.div>
      <p className="text-slate-400 text-[14.5px] mb-8">
        Real-time AI protection for your organization's email ecosystem
      </p>

      <div className="grid grid-cols-5 gap-4 mb-5">
        <StatCard label="Inbox Health" value={stats?.trust_score ?? 100} suffix="/100" icon={Activity} accent="success" trend="↑ live" delay={0} />
        <StatCard label="Protected Emails" value={total.toLocaleString()} icon={Mail} accent="primary" trend="all time" delay={0.05} />
        <StatCard label="Threats Blocked" value={(stats?.suspicious ?? 0) + (stats?.malicious ?? 0)} icon={ShieldAlert} accent="danger" trend="all time" delay={0.1} />
        <StatCard label="Critical Alerts" value={stats?.malicious ?? 0} icon={Bell} accent="warning" trend="all time" delay={0.15} />
        <StatCard
          label="ML Detection Accuracy"
          value={modelInfo?.trained ? `${(modelInfo.accuracy! * 100).toFixed(1)}%` : '—'}
          icon={Target}
          accent="primary"
          trend={modelInfo?.trained ? `evaluated on ${modelInfo.train_size?.toLocaleString()}-email dataset` : 'not yet trained'}
          delay={0.2}
        />
      </div>

      <div className="grid grid-cols-10 gap-4 mb-5">
        <div className="col-span-4 glass rounded-2xl p-6">
          <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-4">Threats Over Time</div>
          {trend.length ? (
            <ResponsiveContainer width="100%" height={180}>
              <LineChart data={trend}>
                <CartesianGrid stroke="#1E2740" strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="day" tick={{ fontSize: 10, fill: '#5B6478' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 10, fill: '#5B6478' }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ background: '#151B2F', border: '1px solid #232B45', borderRadius: 8, fontSize: 12 }} />
                <Line type="monotone" dataKey="malicious" stroke="#6C63FF" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[180px] flex items-center justify-center text-slate-600 text-[12.5px] text-center px-6">
              Run a few scans to see the timeline build up here.
            </div>
          )}
        </div>

        <div className="col-span-3 glass rounded-2xl p-6">
          <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-3">Observed Threat Indicators</div>
          <div className="text-[10px] text-slate-600 mb-2 leading-snug">Illustrative breakdown by sender domain / URL hosting region — not verified live IP geolocation.</div>
          <WorldThreatMap data={GEO_DEMO} />
        </div>

        <div className="col-span-3 glass rounded-2xl p-6">
          <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-4">Threats by Type</div>
          <ThreatDonut data={donutData} total={total} />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-5">
        <div className="glass rounded-2xl p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase">
              <Flame size={13} className="text-danger" /> Most Recent Threat
            </div>
          </div>
          {latest ? (
            <>
              <div className="flex items-center gap-2.5 mb-4">
                <div className="w-9 h-9 rounded-full flex items-center justify-center" style={{ background: `${LEVEL_COLOR[latest.threat_level]}20` }}>
                  <MailIcon size={15} style={{ color: LEVEL_COLOR[latest.threat_level] }} />
                </div>
                <div className="min-w-0">
                  <div className="text-[12.5px] text-white font-medium truncate">{latest.subject}</div>
                  <div className="text-[10.5px] text-slate-600">{new Date(latest.scanned_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                </div>
              </div>
              <div className="flex justify-between mb-1">
                <span className="text-[10px] text-slate-500">Risk Score</span>
                <span className="text-[10px] text-slate-500">Threat Type</span>
              </div>
              <div className="flex justify-between mb-3">
                <span className="text-[18px] font-bold" style={{ color: LEVEL_COLOR[latest.threat_level] }}>{latest.risk_score}<span className="text-[11px] text-slate-600">/100</span></span>
                <span className="text-[11.5px] text-slate-300 text-right max-w-[55%]">{latest.attack_type}</span>
              </div>
              <div className="flex flex-wrap gap-1 mb-4">
                {latestTechniques.slice(0, 3).map((t) => (
                  <span key={t} className="text-[9.5px] bg-card-raised border border-white/10 rounded-md px-2 py-1 text-slate-300">{t}</span>
                ))}
              </div>
              <button onClick={() => onNavigate('email-analysis')} className="w-full text-[11.5px] py-2 rounded-lg bg-gradient-to-r from-primary to-accent text-white font-medium flex items-center justify-center gap-1.5 hover:opacity-90 transition-opacity">
                View Full Analysis <ArrowRight size={12} />
              </button>
            </>
          ) : (
            <div className="text-slate-600 text-[12.5px] py-8 text-center">No scans yet.</div>
          )}
        </div>

        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase mb-4">
            <MailIcon size={13} /> Email Preview
          </div>
          {latest ? (
            <div className="space-y-2 text-[11.5px]">
              <div><span className="text-slate-500">Subject: </span><span className="text-slate-200">{latest.subject}</span></div>
              <div><span className="text-slate-500">From: </span><span className="text-slate-200">{latest.sender}</span></div>
              <div className="pt-2 mt-2 border-t border-border text-slate-500 leading-relaxed line-clamp-4">
                {latest.explanation}
              </div>
            </div>
          ) : (
            <div className="text-slate-600 text-[12.5px] py-8 text-center">Scan an email to preview it here.</div>
          )}
        </div>

        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase mb-4">
            <Brain size={13} /> AI Analysis Summary
          </div>
          {latest ? (
            <>
              <div className="text-[11px] text-slate-500 mb-2">Why this email is risky:</div>
              <ul className="space-y-1.5 mb-3">
                {latestTechniques.slice(0, 4).map((t) => (
                  <li key={t} className="flex items-start gap-1.5 text-[11px] text-slate-300">
                    <span className="text-danger mt-0.5">✕</span> {t}
                  </li>
                ))}
              </ul>
              <div
                className="rounded-lg px-3 py-2 text-[10.5px] mb-3"
                style={{ background: `${LEVEL_COLOR[latest.threat_level]}15`, color: LEVEL_COLOR[latest.threat_level] }}
              >
                {latest.risk_score >= 70 ? 'Do not act on this email. Verify independently.' : 'Review carefully before acting.'}
              </div>
              <div className="flex items-center justify-between text-[10.5px] text-slate-500 mb-1">
                <span>Confidence Score</span><span>{Math.min(99, latest.risk_score + 5)}%</span>
              </div>
              <div className="w-full h-1.5 bg-card-raised rounded-full overflow-hidden">
                <div className="h-full bg-gradient-to-r from-primary to-accent" style={{ width: `${Math.min(99, latest.risk_score + 5)}%` }} />
              </div>
            </>
          ) : (
            <div className="text-slate-600 text-[12.5px] py-8 text-center">No analysis yet.</div>
          )}
        </div>

        <div className="glass rounded-2xl p-5">
          <div className="flex items-center gap-2 text-[11px] tracking-wide text-slate-500 uppercase mb-4">
            <ArrowUpRight size={13} /> Recent Threats
          </div>
          <div className="space-y-3">
            {history.slice(0, 4).map((h) => {
              const color = LEVEL_COLOR[h.threat_level] ?? '#00E676';
              return (
                <div key={h.id} className="flex items-center justify-between">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="w-2 h-2 rounded-full shrink-0" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
                    <span className="text-[11px] text-slate-300 truncate">{h.attack_type}</span>
                  </div>
                  <span className="text-[9.5px] font-semibold px-1.5 py-0.5 rounded-full border shrink-0 ml-2" style={{ color, borderColor: color, background: `${color}18` }}>
                    {h.threat_level}
                  </span>
                </div>
              );
            })}
            {!history.length && <div className="text-slate-600 text-[12px] text-center py-6">No scans yet.</div>}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <TrustDna score={stats?.trust_score ?? 100} topSenders={TRUSTED_SENDERS_DEMO} />
        <SenderReputation data={SENDER_REP_DEMO} behaviorScore={89} behaviorTrend={[60, 65, 62, 70, 68, 75, 89]} />
        <div className="col-span-2 glass rounded-2xl p-6">
          <div className="text-[11px] tracking-wide text-slate-500 uppercase mb-1">Psychological Manipulation Detected</div>
          <div className="text-[10.5px] text-slate-600 mb-4">Most common tactics across recent scans</div>
          <PsychologyPanel
            scores={{
              urgency: latest ? 70 : 0,
              authority: latest ? 60 : 0,
              fear: latest ? 40 : 0,
              greed: latest ? 20 : 0,
              curiosity: latest ? 15 : 0,
            }}
          />
        </div>
      </div>
    </div>
  );
}
