import { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Save } from 'lucide-react';

export default function Settings() {
  const [orgName, setOrgName] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    setOrgName(localStorage.getItem('phishguard_default_org') || '');
  }, []);

  const handleSave = () => {
    localStorage.setItem('phishguard_default_org', orgName);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-8 max-w-2xl">
      <div className="flex items-center gap-2 mb-1">
        <SettingsIcon size={22} className="text-primary" />
        <h1 className="text-2xl font-bold text-white tracking-tight">Settings</h1>
      </div>
      <p className="text-slate-400 text-[13.5px] mb-8">Preferences for this dashboard, saved locally in your browser.</p>

      <div className="glass rounded-2xl p-6">
        <label className="text-[12.5px] text-slate-400 block mb-2">Default organization name</label>
        <p className="text-[11.5px] text-slate-600 mb-3">
          Pre-fills the "Organization name" field on Email Analysis, used for the sender-domain-mismatch check.
        </p>
        <div className="flex gap-3">
          <input
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            placeholder="e.g. Acme Corp"
            className="flex-1 bg-card-raised border border-border rounded-lg px-4 py-2.5 text-[13px] text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-primary/50"
          />
          <button
            onClick={handleSave}
            className="px-5 rounded-lg bg-gradient-to-r from-primary to-accent text-white text-[13px] font-medium flex items-center gap-2 hover:opacity-90 transition-opacity"
          >
            <Save size={14} /> {saved ? 'Saved!' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
}
