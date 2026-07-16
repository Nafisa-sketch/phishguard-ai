import { Search, Bell, Sparkles } from 'lucide-react';

export default function TopBar() {
  return (
    <div className="h-16 border-b border-border flex items-center justify-between px-8 sticky top-0 bg-bg/80 backdrop-blur-md z-10">
      <div className="relative w-80">
        <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search emails, senders, domains..."
          className="w-full bg-card border border-border rounded-lg pl-9 pr-4 py-2 text-[13px] text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-primary/50 transition-colors"
        />
      </div>

      <div className="flex items-center gap-3">
        <button className="flex items-center gap-2 px-3.5 py-2 rounded-lg bg-gradient-to-r from-primary/15 to-accent/10 border border-primary/30 text-[12.5px] text-slate-200 hover:from-primary/25 hover:to-accent/15 transition-all">
          <Sparkles size={14} className="text-accent" />
          Ask PhishGuard AI
        </button>
        <button className="relative w-9 h-9 rounded-lg bg-card border border-border flex items-center justify-center hover:border-primary/40 transition-colors">
          <Bell size={15} className="text-slate-400" />
          <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-danger text-[9px] flex items-center justify-center text-white font-medium">3</span>
        </button>
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center text-[12px] font-semibold text-white">
          N
        </div>
      </div>
    </div>
  );
}
