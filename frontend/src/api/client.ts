import type { AnalyzeResponse, ScanRecord, Stats, TrendPoint } from '../types';

const BASE = '/api';

export async function analyzeEmail(emailText: string, claimedOrg?: string): Promise<AnalyzeResponse> {
  const res = await fetch(`${BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email_text: emailText, claimed_org: claimedOrg }),
  });
  if (!res.ok) throw new Error('Analysis failed');
  return res.json();
}

export async function getHistory(limit = 50): Promise<ScanRecord[]> {
  const res = await fetch(`${BASE}/history?limit=${limit}`);
  const data = await res.json();
  return data.scans;
}

export async function getStats(): Promise<Stats> {
  const res = await fetch(`${BASE}/stats`);
  return res.json();
}

export async function getTrend(days = 7): Promise<TrendPoint[]> {
  const res = await fetch(`${BASE}/trend?days=${days}`);
  const data = await res.json();
  return data.trend;
}

export async function scanQrImage(file: File): Promise<{ findings: { source_filename: string; qr_content: string; is_url: boolean }[] }> {
  const formData = new FormData();
  formData.append('image', file);
  const res = await fetch(`${BASE}/scan-qr`, { method: 'POST', body: formData });
  return res.json();
}

export interface SenderIntel {
  sender: string;
  email_count: number;
  avg_risk: number;
  max_risk: number;
  last_seen: string;
}

export async function getSenders(): Promise<SenderIntel[]> {
  const res = await fetch(`${BASE}/senders`);
  const data = await res.json();
  return data.senders;
}

export async function getAttackStories(minScore = 60): Promise<ScanRecord[]> {
  const res = await fetch(`${BASE}/attack-stories?min_score=${minScore}`);
  const data = await res.json();
  return data.stories;
}

export async function checkUrl(url: string): Promise<{ url: string; suspicious: boolean; flagged_as: string[] }> {
  const res = await fetch(`${BASE}/check-url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });
  return res.json();
}

export interface ThreatFeedItem {
  date_added: string;
  url: string;
  threat_type: string;
  tags: string;
}

export async function getThreatFeed(limit = 15): Promise<ThreatFeedItem[]> {
  const res = await fetch(`${BASE}/threat-feed?limit=${limit}`);
  const data = await res.json();
  return data.threats;
}

export interface IntegrationStatus {
  gmail: { credentials_found: boolean; authorized: boolean; status: string };
}

export async function getIntegrationsStatus(): Promise<IntegrationStatus> {
  const res = await fetch(`${BASE}/integrations/status`);
  return res.json();
}

export interface ModelInfo {
  trained: boolean;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  train_size?: number;
}

export async function getModelInfo(): Promise<ModelInfo> {
  const res = await fetch(`${BASE}/model-info`);
  return res.json();
}

export interface CopilotMessage {
  role: 'user' | 'assistant';
  content: string;
}

export async function askCopilot(message: string, history: CopilotMessage[]): Promise<{ reply?: string; error?: string; message?: string }> {
  const res = await fetch(`${BASE}/copilot/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, history }),
  });
  return res.json();
}
