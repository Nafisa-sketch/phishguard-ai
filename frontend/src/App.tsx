import { useState } from 'react';
import Sidebar from './components/Sidebar';
import TopBar from './components/TopBar';
import CopilotChat from './components/CopilotChat';
import MissionControl from './pages/MissionControl';
import EmailAnalysis from './pages/EmailAnalysis';
import QrShield from './pages/QrShield';
import Reports from './pages/Reports';
import SenderIntelligence from './pages/SenderIntelligence';
import UrlIntelligence from './pages/UrlIntelligence';
import TrustDnaPage from './pages/TrustDnaPage';
import AttackStories from './pages/AttackStories';
import ThreatIntelligence from './pages/ThreatIntelligence';
import Settings from './pages/Settings';
import Integrations from './pages/Integrations';

export default function App() {
  const [page, setPage] = useState('mission-control');
  const [copilotOpen, setCopilotOpen] = useState(false);

  return (
    <div className="flex min-h-screen bg-bg">
      <Sidebar activePage={page} onNavigate={setPage} onOpenCopilot={() => setCopilotOpen(true)} />
      <div className="flex-1 min-w-0">
        <TopBar onOpenCopilot={() => setCopilotOpen(true)} />
        {page === 'mission-control' && <MissionControl onNavigate={setPage} />}
        {page === 'email-analysis' && <EmailAnalysis />}
        {page === 'qr-shield' && <QrShield />}
        {page === 'reports' && <Reports />}
        {page === 'sender-intelligence' && <SenderIntelligence />}
        {page === 'url-intelligence' && <UrlIntelligence />}
        {page === 'trust-dna' && <TrustDnaPage />}
        {page === 'attack-stories' && <AttackStories />}
        {page === 'threat-intelligence' && <ThreatIntelligence />}
        {page === 'settings' && <Settings />}
        {page === 'integrations' && <Integrations />}
      </div>
      <CopilotChat open={copilotOpen} onClose={() => setCopilotOpen(false)} />
    </div>
  );
}
