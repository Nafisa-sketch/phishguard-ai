# Architecture

## Pipeline

```
Email input (paste text or .eml upload)
        │
        ▼
  src/parser.py          → extracts sender, body, links, images
        │
        ▼
  src/qr_detector.py     → finds & decodes QR codes in images
        │
        ▼
  src/features.py        → turns text + metadata into signals
        │                   (urgency words, domain mismatch, etc.)
        ▼
  src/detector.py         → rule-based + ML classification
        │
        ▼
  src/explainer.py        → turns signals into a plain-English reason
        │
        ▼
  app/dashboard.py        → shows risk score, badges, explanation
```

## Modules

| File | Responsibility |
|---|---|
| `src/parser.py` | Parse raw email into structured fields |
| `src/qr_detector.py` | Extract images, decode QR codes, return URLs found |
| `src/features.py` | Extract detection features (keywords, domain checks, etc.) |
| `src/detector.py` | Combine features into a classification + risk score |
| `src/explainer.py` | Generate human-readable explanation from detection results |
| `app/dashboard.py` | Streamlit UI |

## Design principle

Each module takes plain data in and returns plain data out (dictionaries),
so every piece can be tested on its own without running the whole pipeline.
