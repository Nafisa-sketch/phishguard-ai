<img width="1867" height="882" alt="Screenshot 2026-07-21 001658" src="https://github.com/user-attachments/assets/31a892f7-733c-4387-972e-588a1bb53801" />
# PhishGuard AI

**AI Email Trust Intelligence Platform** — detects phishing, spear phishing,
whaling, business email compromise (BEC), QR-code phishing ("quishing"),
callback phishing, and device-code (OAuth token theft) attacks, then
explains *why* an email is dangerous in plain language.

Built as a learning/portfolio project combining a rule-based detection
engine, a real trained machine learning classifier, and a full-stack
web dashboard.

## What it detects

| Attack type | How |
|---|---|
| Generic / Spear Phishing | Urgency, authority, and request-pattern keyword analysis |
| Business Email Compromise (BEC) | Authority + money/credential request + sender domain mismatch |
| Whaling | Same as BEC, specifically impersonating senior executives |
| Callback Phishing | Phone number + urgency language ("call us immediately") |
| Quishing (QR code phishing) | Decodes QR codes in email images, checks the hidden URL |
| Device Code Phishing | Detects real Microsoft/Google/GitHub device-login links paired with "enter this code" language — a 2024-2025 attack technique that steals OAuth tokens without ever touching a password |
| Brand Impersonation | Display name claims a known brand (PayPal, Microsoft, etc.) but the sending domain doesn't match |
| **AI-Detected Suspicious Pattern** | A trained ML model (see below) flags emails whose *wording/style* resembles phishing even when no rule fired |

Every email is also checked for:
- SPF / DKIM / DMARC authentication results (when available, e.g. from an uploaded `.eml` file)
- Whether the sender has emailed you before (first-time-sender signal)
- Whether the sender's domain is a well-known, trusted service (reduces false positives)
- Psychological manipulation levers (urgency, authority, fear, greed, curiosity)

## Machine Learning model

A TF-IDF + Random Forest classifier trained on **82,486 real emails**
(a combined Kaggle dataset built from Enron, Nazario, SpamAssassin, CEAS,
and Nigerian-fraud corpora):

- **Accuracy:** 96.6%
- **Precision:** 94.8%
- **Recall:** 98.9%
- **F1 Score:** 0.968

The ML model and the rule-based engine work together: rules catch
*structural* evidence (bad domains, malicious QR codes, failed
authentication) the ML model can't see, while the ML model catches
*wording/style* patterns that fixed keyword rules miss. See
`train_model.py` to retrain on your own data.

## Architecture

```
React frontend (Vite + TypeScript + Tailwind)
        │  HTTP (fetch)
        ▼
Flask API (api.py)
        │
        ▼
Python detection engine (src/)
  ├─ parser.py           — email parsing
  ├─ features.py         — rule-based signal extraction
  ├─ qr_detector.py       — QR code decoding (OpenCV)
  ├─ email_auth.py        — SPF/DKIM/DMARC checking
  ├─ ml_classifier.py      — trained ML model (TF-IDF + Random Forest)
  ├─ detector.py           — combines everything into a risk score
  ├─ database.py            — SQLite scan history
  ├─ gmail_client.py         — real Gmail inbox integration (OAuth, read-only)
  └─ threat_feed.py          — live threat intel (URLhaus)
```

## Dashboard pages

- **Mission Control** — live stats, threat timeline, world map (illustrative), threat-type breakdown, Trust DNA, psychology panel
- **Email Analysis** — paste an email or upload a `.eml` file for full analysis
- **QR Shield** — upload a QR code image directly
- **Sender Intelligence** — every sender you've received email from, ranked by risk
- **URL Intelligence** — check any single URL for structural red flags
- **Trust DNA** — behavioral trust profile built from your own scan history
- **Attack Stories** — high-risk scans presented as plain-language narratives
- **Threat Intelligence** — live global feed from URLhaus (abuse.ch)
- **Reports** — full scan history table
- **Settings / Integrations** — preferences and Gmail connection status

## How to run

### 1. Backend (Python)

```bash
pip install -r requirements.txt
pip install flask flask-cors
python api.py
```
Runs on `http://localhost:5000`.

### 2. Frontend (React)

```bash
cd frontend
npm install --legacy-peer-deps
npm run dev
```
Runs on `http://localhost:5173`. Open this in your browser.

### 3. (Optional) Train the ML model yourself

Download the ["Phishing Email Dataset"](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset)
from Kaggle, unzip it into `data/raw/Phishing_Email/`, then:

```bash
python train_model.py
```

### 4. (Optional) Connect a real Gmail inbox

Set up OAuth credentials in Google Cloud Console (Gmail API, Desktop app
credentials), save `credentials.json` in the project root, then:

```bash
python scan_inbox.py
```

First run opens a browser login/consent screen. After that, your inbox
scans are saved to the same database the dashboard reads from.

## Honest limitations

This is a learning/portfolio project, not production security software:

- The world map on Mission Control is illustrative — real sender
  geolocation requires a live threat-intelligence feed, which most
  pasted email text doesn't provide enough data for.
- The "AI Copilot" chat button in the sidebar is a static UI element,
  not yet wired to a real LLM.
- False-positive rates were reduced through iterative testing on a
  real personal inbox (see commit history), but no detector — rule-based
  or ML — can guarantee 100% accuracy.
- SPF/DKIM/DMARC checking only works when real email headers are
  available (uploaded `.eml` files), not plain pasted text.

## Tech stack

Python, Flask, scikit-learn, OpenCV, SQLite, React, TypeScript, Vite,
TailwindCSS, Framer Motion, Recharts, Google Gmail API.
