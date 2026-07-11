# PhishGuard AI

An AI-powered assistant that detects phishing, spear phishing, business email
compromise (BEC), and QR-code phishing ("quishing") in emails — and explains
*why* an email is dangerous in plain language.

## Why this project exists

Most phishing filters catch obvious spam. They miss **spear phishing** 
personalized attacks that use a real name, role, or company detail to look
legitimate  and **quishing**, where attackers hide a malicious link inside a
QR code image to bypass link scanners entirely (a technique the FBI flagged
in active nation-state campaigns in January 2026).

PhishGuard AI is a learning project + portfolio piece that builds a working
detector for all of these, with a focus on the QR-code detection angle,
which most existing consumer/small-business tools don't cover well.

## Status

🚧 Work in progress. Build phases:

- [x] Phase 0 — Project setup
- [ ] Phase 1 — Email parsing
- [ ] Phase 2 — Dataset collection
- [ ] Phase 3 — Rule-based detector
- [ ] Phase 4 — QR / quishing detection
- [ ] Phase 5 — ML classifier
- [ ] Phase 6 — Explanation layer
- [ ] Phase 7 — Dashboard
- [ ] Phase 8 — Tests + CI

## How to run (once built)

```bash
pip install -r requirements.txt
streamlit run app/dashboard.py
```

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for how the pieces fit together.

## Limitations

This is a learning/portfolio prototype, not production security software.
It has not been evaluated on real-world attack traffic at scale, and
false positive/negative rates will be documented honestly once testing
is complete (Phase 8).
