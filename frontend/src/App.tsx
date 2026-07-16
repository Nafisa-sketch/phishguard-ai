import { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import MissionControl from './pages/MissionControl';
import EmailAnalysis from './pages/EmailAnalysis';
import QrShield from './pages/QrShield';
import Reports from './pages/Reports';
import ComingSoon from './pages/ComingSoon';

const PAGE_TITLES: Record<string, string> = {
  'sender-intelligence': 'Sender Intelligence',
  'url-intelligence': 'URL Intelligence',
  'trust-dna': 'Trust DNA',
  'attack-stories': 'Attack Stories',
  'threat-intelligence': 'Threat Intelligence',
  settings: 'Settings',
  integrations: 'Integrations',
};

export default function App() {
  const [page, setPage] = useState('mission-control');

  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar activePage={page} onNavigate={setPage} />
      <div className="flex-1 min-w-0">
        <TopBar />
        {page === 'mission-control' && <MissionControl onNavigate={setPage} />}
        {page === 'email-analysis' && <EmailAnalysis />}
        {page === 'qr-shield' && <QrShield />}
        {page === 'reports' && <Reports />}
        {PAGE_TITLES[page] && <ComingSoon title={PAGE_TITLES[page]} />}
      </div>
    </div>
  );
}
