import {
  ShieldCheck, Mail, QrCode, UserSearch, Link2, Fingerprint,
  BookOpen, Radar, FileBarChart, Settings, Puzzle, Sparkles, ArrowRight,
} from 'lucide-react';

const NAV_ITEMS = [
  { key: 'mission-control', label: 'Mission Control', icon: ShieldCheck, available: true },
  { key: 'email-analysis', label: 'Email Analysis', icon: Mail, available: true },
  { key: 'qr-shield', label: 'QR Shield', icon: QrCode, available: true },
  { key: 'sender-intelligence', label: 'Sender Intelligence', icon: UserSearch, available: false },
  { key: 'url-intelligence', label: 'URL Intelligence', icon: Link2, available: false },
  { key: 'trust-dna', label: 'Trust DNA', icon: Fingerprint, available: false },
  { key: 'attack-stories', label: 'Attack Stories', icon: BookOpen, available: false },
  { key: 'threat-intelligence', label: 'Threat Intelligence', icon: Radar, available: false },
  { key: 'reports', label: 'Reports', icon: FileBarChart, available: true },
  { key: 'settings', label: 'Settings', icon: Settings, available: false },
  { key: 'integrations', label: 'Integrations', icon: Puzzle, available: false },
];

interface SidebarProps {
  activePage: string;
  onNavigate: (page: string) => void;
}

export default function Sidebar({ activePage, onNavigate }: SidebarProps) {
  return (
    <aside className="w-64 shrink-0 h-screen sticky top-0 bg-card/80 border-r border-border flex flex-col">
      <div className="px-6 py-6 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center shadow-lg shadow-primary/20">
          <ShieldCheck size={18} className="text-white" />
        </div>
        <div>
          <div className="font-semibold text-[15px] tracking-tight text-white">PhishGuard AI</div>
          <div className="text-[10px] text-slate-500 tracking-wide">AI Identity Attack Intelligence</div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-2 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.key;
          return (
            <button
              key={item.key}
              onClick={() => item.available && onNavigate(item.key)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-[13.5px] transition-all
                ${isActive
                  ? 'bg-gradient-to-r from-primary/20 to-accent/10 text-white border border-primary/30'
                  : item.available
                    ? 'text-slate-400 hover:text-white hover:bg-white/5'
                    : 'text-slate-600 cursor-not-allowed'}`}
            >
              <Icon size={16} strokeWidth={1.75} />
              <span className="flex-1 text-left">{item.label}</span>
              {!item.available && (
                <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-white/5 text-slate-600">Soon</span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="px-4 py-4 border-t border-border">
        {/* NOTE: this is a static UI element for now -- wiring it to a real
            LLM would need an API key and a backend chat endpoint. It's
            included here to match the reference layout, but doesn't
            actually answer questions yet. */}
        <div className="glass rounded-xl p-4 mb-3">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Sparkles size={13} className="text-white" />
            </div>
            <span className="text-[12.5px] font-medium text-white">AI Copilot</span>
          </div>
          <p className="text-[11px] text-slate-500 leading-snug mb-3">
            Ask anything about threats, emails, senders or URLs...
          </p>
          <button className="w-full text-[11.5px] py-2 rounded-lg bg-gradient-to-r from-primary to-accent text-white font-medium flex items-center justify-center gap-1.5 hover:opacity-90 transition-opacity">
            Ask PhishGuard AI <ArrowRight size={12} />
          </button>
        </div>
        <div className="text-[10px] text-slate-600 tracking-wide">
          PhishGuard AI · Learning &amp; Portfolio Project
        </div>
      </div>
    </aside>
  );
}
