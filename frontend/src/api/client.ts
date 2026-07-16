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
