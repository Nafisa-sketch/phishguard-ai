# Architecture

## System overview

```
┌─────────────────────────────────────────────────────────────┐
│  React Frontend (Vite + TypeScript + TailwindCSS)             │
│  frontend/src/                                                 │
│    ├─ pages/          Mission Control, Email Analysis,         │
│    │                  QR Shield, Sender/URL Intelligence,      │
│    │                  Trust DNA, Attack Stories,                │
│    │                  Threat Intelligence, Reports, Settings    │
│    ├─ components/     Sidebar, TopBar, charts, gauges           │
│    └─ api/client.ts   fetch() calls to the Flask API            │
└───────────────────────────┬─────────────────────────────────┘
                             │ HTTP (JSON)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Flask API (api.py)                                             │
│    /api/analyze          — full email analysis                  │
│    /api/scan-qr           — standalone QR image scan             │
│    /api/senders            — sender intelligence aggregation      │
│    /api/check-url           — single URL structural check          │
│    /api/threat-feed          — live feed from URLhaus               │
│    /api/model-info            — trained ML model metrics             │
│    /api/history, /api/stats,   /api/trend, /api/integrations/status  │
└───────────────────────────┬─────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Python detection engine (src/)                                 │
│                                                                   │
│  parser.py ──► features.py ──► detector.py ──► explanation       │
│                    │                 ▲                            │
│              (rule-based           │                              │
│               signals)      ml_classifier.py                      │
│                              (trained model)                       │
│                                                                     │
│  qr_detector.py    — OpenCV QR decoding                            │
│  email_auth.py      — SPF/DKIM/DMARC header parsing                 │
│  gmail_client.py      — Gmail OAuth + inbox fetching                 │
│  threat_feed.py         — URLhaus live feed                          │
│  database.py              — SQLite persistence                       │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
                  data/processed/phishguard.db
                  (every scan's full result, for
                   history, trends, and sender intel)
```

## Detection pipeline (what happens on one `analyze_email()` call)

1. **parser.py** turns raw email text or a `.eml` file into a
   structured dict: `{sender, subject, body, links, images}`.
2. **features.py** runs ~15 independent rule-based checks against that
   dict (urgency wording, sender domain, QR presence via
   `qr_detector.py`, typosquatting, display-name spoofing, dangerous
   attachments, reply-to mismatch, device-code phishing patterns, and
   more), returning one combined dict of booleans/values.
3. **email_auth.py** separately checks SPF/DKIM/DMARC headers, when
   available (only meaningful for uploaded `.eml` files with intact
   headers).
4. **database.py** is queried for whether this sender has emailed the
   user before (first-time-sender signal).
5. **detector.py** combines all of the above into:
   - a **risk score** (0-100), built from two separate pools:
     "wording" evidence (urgency/authority/request keywords — weak on
     their own, heavily discounted for senders on the trusted-domain
     allowlist) and "structural" evidence (bad domains, malicious
     links, QR codes, failed authentication, dangerous attachments —
     never discounted, since these are concrete, not just wording)
   - an **attack-type classification** (Whaling, BEC, Quishing, Device
     Code Phishing, Brand Impersonation, etc.), chosen by which
     combination of signals fired
   - a list of specific **techniques detected**
6. **ml_classifier.py** blends in a trained TF-IDF + Random Forest
   model's prediction. If the rules found nothing but the ML model is
   confident the wording resembles phishing, that's surfaced as its
   own "AI-Detected Suspicious Pattern" category rather than silently
   dropped. If rules already found a specific attack, the ML score
   nudges the final number rather than overriding the rule-based
   classification (which carries the specific evidence).
7. **build_explanation()** turns the final result into a plain-English
   paragraph for the "Why This Email Was Flagged" panel.
8. The full result is saved to the database via `database.save_scan()`,
   which is what powers the history, trend charts, and sender
   intelligence pages.

## Design principle

Every module takes plain data in and returns plain data out
(dictionaries), so each piece can be tested independently — see
`tests/test_features.py` and `tests/test_detector.py` (29 tests,
run with `pytest tests/ -v`).

## Two parallel entry points into the same engine

- **Dashboard** (`api.py` → React) — for interactively pasting/
  uploading one email at a time.
- **`scan_inbox.py`** — for batch-scanning a real Gmail inbox via
  `gmail_client.py`. Both paths call the exact same
  `detector.analyze_email()` function and save to the exact same
  database, so results are consistent regardless of how an email
  entered the system.
