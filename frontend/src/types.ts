export interface ParsedEmail {
  sender: string | null;
  subject: string | null;
  body: string;
  links: string[];
  images: unknown[];
}

export interface TextFeatures {
  urgency_detected: boolean;
  urgency_phrases: string[];
  authority_detected: boolean;
  authority_phrases: string[];
  request_detected: boolean;
  request_phrases: string[];
  domain_suspicious: boolean;
  reason: string | null;
  suspicious_links_found: boolean;
  suspicious_links: string[];
  executive_impersonation_detected: boolean;
  callback_detected: boolean;
  phone_number_found: boolean;
}

export interface QrSignal {
  qr_detected: boolean;
  qr_urls?: string[];
  risk_note: string | null;
}

export interface AuthSignal {
  auth_checked: boolean;
  auth_failed: boolean;
  summary: string;
}

export interface SenderHistory {
  seen_before: boolean;
  previous_count: number;
}

export interface AnalysisResult {
  risk_score: number;
  threat_level: 'HIGH' | 'MEDIUM' | 'LOW' | 'MINIMAL';
  attack_type: string;
  techniques_detected: string[];
  details: {
    text_features: TextFeatures;
    qr_signal: QrSignal;
    auth_signal: AuthSignal;
    sender_history: SenderHistory;
  };
}

export interface Psychology {
  urgency: number;
  authority: number;
  curiosity: number;
  greed: number;
  fear: number;
}

export interface AnalyzeResponse {
  parsed: ParsedEmail;
  result: AnalysisResult;
  explanation: string;
  psychology: Psychology;
}

export interface ScanRecord {
  id: number;
  scanned_at: string;
  sender: string | null;
  subject: string | null;
  risk_score: number;
  threat_level: string;
  attack_type: string;
  techniques: string;
  explanation: string;
}

export interface Stats {
  total: number;
  safe: number;
  suspicious: number;
  malicious: number;
  trust_score: number;
}

export interface TrendPoint {
  day: string;
  safe: number;
  suspicious: number;
  malicious: number;
}
