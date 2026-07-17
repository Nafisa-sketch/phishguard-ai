"""
dashboard.py

The visual interface for PhishGuard AI. Single-page, focused design:
paste an email, click analyze, see the result. Violet/magenta dark
theme with a prominent animated QR-code panel and an email-client-style
preview of the analyzed email.

Run with:
    streamlit run app/dashboard.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from src import parser
from src import detector
from src import database

database.init_db()


st.set_page_config(
    page_title="PhishGuard AI — Inbox Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-deep: #0B0A14;
    --bg-panel: #14111F;
    --bg-panel-raised: #191530;
    --border: #241F38;
    --border-bright: #3D3560;
    --text-primary: #EDEBF7;
    --text-muted: #B3A9CC;
    --text-dim: #7C6FA8;
    --text-dimmer: #5C5480;
    --violet: #A78BFA;
    --violet-dim: rgba(167, 139, 250, 0.12);
    --pink: #F472B6;
    --pink-dim: rgba(244, 114, 182, 0.12);
    --red: #F0495C;
    --red-dim: rgba(240, 73, 92, 0.12);
    --safe: #3ECF8E;
    --safe-dim: rgba(62, 207, 142, 0.12);
}

#MainMenu, footer, header {visibility: hidden;}
.stApp {
    background:
        radial-gradient(ellipse 800px 450px at 10% -10%, rgba(167, 139, 250, 0.07), transparent),
        var(--bg-deep);
}
.block-container { padding-top: 2.5rem; padding-bottom: 3rem; max-width: 1100px; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--text-primary); }

@keyframes pg-fadeup { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
@keyframes pg-glow { 0%, 100% { box-shadow: 0 0 10px rgba(167,139,250,0.2); } 50% { box-shadow: 0 0 20px rgba(167,139,250,0.45); } }
@keyframes pg-pulse { 0%, 100% { opacity: 0.55; transform: scale(1); } 50% { opacity: 1; transform: scale(1.12); } }
@keyframes pg-scanline { 0% { top: 4%; } 50% { top: 90%; } 100% { top: 4%; } }

.pg-header-left { display: flex; align-items: center; gap: 12px; animation: pg-fadeup 0.4s ease both; }
.pg-shield {
    width: 38px; height: 38px; border-radius: 8px;
    background: var(--violet-dim); border: 1px solid var(--border-bright);
    display: flex; align-items: center; justify-content: center; font-size: 19px; flex-shrink: 0;
    animation: pg-glow 3s ease-in-out infinite;
}
.pg-title { font-family: 'Space Grotesk', sans-serif; font-size: 22px; font-weight: 600; color: var(--text-primary); margin: 0; line-height: 1.1; }
.pg-subtitle { font-family: 'JetBrains Mono', monospace; font-size: 10px; color: var(--violet); letter-spacing: 0.1em; text-transform: uppercase; margin: 2px 0 0 0; }
.pg-tagline { color: var(--text-muted); font-size: 14px; margin: 18px 0 24px 0; max-width: 620px; line-height: 1.55; animation: pg-fadeup 0.4s ease 0.05s both; }

.pg-panel {
    background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px;
    padding: 20px 22px; margin-bottom: 14px; animation: pg-fadeup 0.4s ease both;
}
.pg-panel-label {
    font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase;
    color: var(--text-dim); margin-bottom: 12px; display: flex; align-items: center; gap: 7px;
}

.stTextArea textarea, .stTextInput input {
    background: var(--bg-panel-raised) !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
    color: var(--text-primary) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important;
}
.stTextArea textarea:focus, .stTextInput input:focus { border-color: var(--violet) !important; box-shadow: 0 0 0 1px var(--violet) !important; }
.stTextInput label, .stTextArea label { font-family: 'IBM Plex Sans', sans-serif !important; color: var(--text-muted) !important; font-size: 13px !important; }
.stButton button {
    background: linear-gradient(135deg, var(--violet), #8B6FE0) !important; color: #1A1030 !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-family: 'Space Grotesk', sans-serif !important;
    padding: 10px 26px !important; transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton button:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(167, 139, 250, 0.35); }

.email-row { display: flex; align-items: center; gap: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--border); margin-bottom: 10px; margin-top: 10px; }
.email-avatar {
    width: 34px; height: 34px; border-radius: 50%; background: var(--bg-panel-raised);
    display: flex; align-items: center; justify-content: center; color: var(--violet); flex-shrink: 0;
    font-family: 'JetBrains Mono', monospace; font-size: 13px;
}
.email-from { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.email-subject { font-size: 15px; color: var(--text-primary); font-weight: 600; margin-top: 2px; }
.email-body { font-size: 13px; color: var(--text-muted); line-height: 1.7; max-height: 160px; overflow-y: auto; white-space: pre-wrap; }

.qr-panel {
    background: linear-gradient(135deg, var(--pink-dim), var(--bg-panel));
    border: 1.5px solid var(--pink); border-radius: 12px; padding: 18px 20px; margin-bottom: 14px;
    box-shadow: 0 0 22px rgba(244, 114, 182, 0.12); animation: pg-fadeup 0.4s ease both;
}
.qr-label { display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
.qr-label-text { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; letter-spacing: 0.08em; color: var(--pink); text-transform: uppercase; font-weight: 600; }
.qr-visual-wrap { position: relative; width: 92px; height: 92px; margin: 0 auto; flex-shrink: 0; }
.qr-visual-border { position: absolute; inset: 0; border: 2px solid var(--pink); border-radius: 8px; }
.qr-scan-line {
    position: absolute; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, transparent, var(--pink), transparent);
    box-shadow: 0 0 10px 2px rgba(244, 114, 182, 0.6);
    animation: pg-scanline 2.6s ease-in-out infinite;
}
.qr-warning-dot {
    position: absolute; top: -9px; right: -9px; width: 20px; height: 20px; border-radius: 50%;
    background: var(--pink); display: flex; align-items: center; justify-content: center;
    animation: pg-pulse 1.3s ease-in-out infinite;
}
.qr-url-box {
    font-family: 'JetBrains Mono', monospace; font-size: 11px; color: var(--pink);
    background: var(--bg-deep); border: 1px solid #3D2438; border-radius: 6px;
    padding: 7px 10px; word-break: break-all;
}

.score-readout { font-family: 'JetBrains Mono', monospace; font-size: 32px; font-weight: 600; line-height: 1.1; }
.score-label { font-family: 'JetBrains Mono', monospace; font-size: 9.5px; color: var(--text-dim); letter-spacing: 0.1em; margin-bottom: 6px; }
.threat-badge {
    display: inline-flex; align-items: center; gap: 7px; padding: 6px 13px; border-radius: 4px;
    font-family: 'JetBrains Mono', monospace; font-size: 10.5px; font-weight: 600; letter-spacing: 0.06em; border: 1px solid;
    margin-top: 8px;
}
.attack-type { font-size: 14.5px; font-weight: 500; color: var(--text-primary); margin-top: 5px; }

.object-row { display: flex; align-items: center; gap: 10px; padding: 4px 0; }
.object-dot { width: 8px; height: 8px; border-radius: 2px; flex-shrink: 0; }
.object-name { font-family: 'JetBrains Mono', monospace; font-size: 11.5px; color: var(--text-primary); }

.detail-row { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid var(--border); font-size: 13px; gap: 12px; }
.detail-row:last-child { border-bottom: none; }
.detail-key { color: var(--text-muted); flex-shrink: 0; }
.detail-val { font-family: 'JetBrains Mono', monospace; color: var(--text-primary); text-align: right; word-break: break-word; }

.rec-box { border-radius: 10px; padding: 16px 18px; font-size: 13.5px; line-height: 1.6; border: 1px solid; margin-top: 4px; }
.explain-box { font-size: 13px; color: var(--text-muted); line-height: 1.7; margin: 0; }

.pg-footer {
    margin-top: 36px; padding-top: 16px; border-top: 1px solid var(--border);
    font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: var(--text-dimmer);
    display: flex; justify-content: space-between; flex-wrap: wrap; gap: 8px;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="pg-header-left">
        <div class="pg-shield">🛡️</div>
        <div>
            <p class="pg-title">PhishGuard AI</p>
            <p class="pg-subtitle">Inbox Security Scanner</p>
        </div>
    </div>
    <p class="pg-tagline">
        Detects phishing, spear phishing, business email compromise, and
        QR-code (quishing) threats — with a plain-language breakdown of
        exactly why an email is dangerous.
    </p>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
st.markdown('<div class="pg-panel-label">📧 Email Input</div>', unsafe_allow_html=True)

input_mode = st.radio(
    "Input method",
    ["Paste email text", "Upload .eml file (enables SPF/DKIM/DMARC check)"],
    horizontal=True,
    label_visibility="collapsed",
)

uploaded_eml = None
col_a, col_b = st.columns([2, 1])
with col_a:
    if input_mode == "Paste email text":
        email_text = st.text_area(
            "Paste the full email",
            height=200,
            placeholder=(
                "From: ceo.company@gmail.com\n"
                "Subject: Urgent wire transfer needed\n\n"
                "Hi Sarah, as requested by the Finance Department, please wire "
                "transfer $5,000 immediately before 5 PM today..."
            ),
            label_visibility="collapsed",
        )
    else:
        uploaded_eml = st.file_uploader("Upload .eml file", type=["eml"], label_visibility="collapsed")
        st.caption("Uploading the real .eml file (not pasted text) lets us check SPF/DKIM/DMARC authentication headers.")
        email_text = ""
with col_b:
    claimed_org = st.text_input("Organization name (optional)", placeholder="e.g. Acme Corp")
    st.write("")
    analyze_clicked = st.button("Run Scan  →", type="primary", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

LEVEL_COLORS = {
    "HIGH":    {"main": "var(--red)",    "dim": "var(--red-dim)"},
    "MEDIUM":  {"main": "var(--pink)",   "dim": "var(--pink-dim)"},
    "LOW":     {"main": "var(--pink)",   "dim": "var(--pink-dim)"},
    "MINIMAL": {"main": "var(--safe)",   "dim": "var(--safe-dim)"},
}

QR_SVG = """
<svg width="92" height="92" viewBox="0 0 64 64" style="padding:8px; box-sizing:border-box; position:relative; z-index:1;">
<g fill="#A78BFA">
<rect x="4" y="4" width="16" height="16"/><rect x="8" y="8" width="8" height="8" fill="#0B0A14"/>
<rect x="44" y="4" width="16" height="16"/><rect x="48" y="8" width="8" height="8" fill="#0B0A14"/>
<rect x="4" y="44" width="16" height="16"/><rect x="8" y="48" width="8" height="8" fill="#0B0A14"/>
<rect x="26" y="4" width="6" height="6"/><rect x="26" y="26" width="6" height="6"/><rect x="34" y="26" width="6" height="6"/>
<rect x="26" y="34" width="6" height="6"/><rect x="44" y="34" width="6" height="6"/><rect x="26" y="44" width="6" height="6"/>
<rect x="44" y="52" width="6" height="6"/><rect x="34" y="44" width="6" height="6"/>
</g>
</svg>
"""

if analyze_clicked:
    raw_email_text = None
    parsed = None

    if input_mode == "Paste email text":
        if not email_text.strip():
            st.warning("Paste an email above before running a scan.")
        else:
            raw_email_text = email_text
            parsed = parser.parse_raw_text(email_text)
    else:
        if not uploaded_eml:
            st.warning("Upload a .eml file above before running a scan.")
        else:
            eml_bytes = uploaded_eml.read()
            raw_email_text = eml_bytes.decode("utf-8", errors="ignore")
            parsed = parser.parse_eml_bytes(eml_bytes)

    if parsed:
        result = detector.analyze_email(parsed, claimed_org=claimed_org or None, raw_email_text=raw_email_text)
        explanation = detector.build_explanation(result)
        database.save_scan(parsed, result, explanation)

        level = result["threat_level"]
        colors = LEVEL_COLORS.get(level, LEVEL_COLORS["MINIMAL"])
        score = result["risk_score"]
        qr_signal = result["details"]["qr_signal"]
        text_features = result["details"]["text_features"]

        sender = parsed.get("sender") or "Unknown sender"
        first_letter = sender[0].upper() if sender and sender[0].isalpha() else "?"
        body_preview = (parsed.get("body") or "").strip()

        st.markdown(
            f"""
            <div class="pg-panel">
                <div class="pg-panel-label">📧 Uploaded Email</div>
                <div class="email-row">
                    <div class="email-avatar">{first_letter}</div>
                    <div style="flex:1;">
                        <div class="email-from">{sender}</div>
                        <div class="email-subject">{parsed.get('subject') or '(no subject)'}</div>
                    </div>
                </div>
                <div class="email-body">{body_preview}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if qr_signal["qr_detected"]:
            decoded_url = qr_signal.get("qr_urls", ["(non-URL content)"])[0]
            st.markdown(
                f"""
                <div class="qr-panel">
                    <div class="qr-label">
                        <span style="color:var(--pink); font-size:16px;">▣</span>
                        <span class="qr-label-text">QR Code Threat Detected · Quishing</span>
                    </div>
                    <div style="display:grid; grid-template-columns:100px 1fr; gap:18px; align-items:center;">
                        <div class="qr-visual-wrap">
                            <div class="qr-visual-border"></div>
                            {QR_SVG}
                            <div class="qr-scan-line"></div>
                            <div class="qr-warning-dot">⚠</div>
                        </div>
                        <div>
                            <div style="font-size:12.5px; color:var(--text-primary); line-height:1.6; margin-bottom:8px;">{qr_signal["risk_note"]}</div>
                            <div class="score-label">DECODED DESTINATION</div>
                            <div class="qr-url-box">→ {decoded_url}</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            f"""
            <div class="pg-panel">
                <div class="pg-panel-label">📊 Scan Result</div>
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:20px; align-items:center;">
                    <div>
                        <div class="score-label">RISK SCORE</div>
                        <div class="score-readout" style="color:{colors['main']}">{score}<span style="font-size:14px; color:var(--text-dimmer);">/100</span></div>
                        <div class="threat-badge" style="color:{colors['main']}; border-color:{colors['main']}; background:{colors['dim']};">
                            ● {level} RISK
                        </div>
                    </div>
                    <div>
                        <div class="score-label">ATTACK CATEGORY</div>
                        <div class="attack-type">{result['attack_type']}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">🎯 Objects Detected In Scan</div>', unsafe_allow_html=True)
            if result["techniques_detected"]:
                for t in result["techniques_detected"]:
                    dot_color = "var(--red)" if "Domain" in t or "QR" in t else "var(--pink)"
                    st.markdown(
                        f'<div class="object-row"><div class="object-dot" style="background:{dot_color};"></div>'
                        f'<span class="object-name">{t}</span></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown('<span style="color:var(--text-muted); font-size:13px;">No flagged objects. Clean scan.</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">👤 Sender Analysis</div>', unsafe_allow_html=True)
            domain_status = "⚠ Suspicious" if text_features.get("domain_suspicious") else "✓ No issues found"
            st.markdown(
                f'<div class="detail-row"><span class="detail-key">Domain Check</span><span class="detail-val">{domain_status}</span></div>',
                unsafe_allow_html=True,
            )
            if text_features.get("domain_suspicious"):
                st.markdown(
                    f'<p style="color:var(--text-muted); font-size:12px; margin-top:10px;">{text_features["reason"]}</p>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        col_auth, col_history = st.columns([1, 1])

        with col_auth:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">🔐 Authentication Check (SPF/DKIM/DMARC)</div>', unsafe_allow_html=True)
            auth_result = result["details"]["auth_result"]
            auth_signal = result["details"]["auth_signal"]
            if not auth_signal["auth_checked"]:
                st.markdown('<span style="color:var(--text-muted); font-size:12.5px;">No authentication headers available (normal for pasted text — upload the .eml file to check this).</span>', unsafe_allow_html=True)
            else:
                badge_color = "var(--red)" if auth_signal["auth_failed"] else "var(--safe)"
                st.markdown(
                    f'<div class="detail-row"><span class="detail-key">SPF</span><span class="detail-val">{auth_result["spf"].upper()}</span></div>'
                    f'<div class="detail-row"><span class="detail-key">DKIM</span><span class="detail-val">{auth_result["dkim"].upper()}</span></div>'
                    f'<div class="detail-row"><span class="detail-key">DMARC</span><span class="detail-val">{auth_result["dmarc"].upper()}</span></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f'<p style="color:{badge_color}; font-size:12px; margin-top:10px;">{auth_signal["summary"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_history:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">🕐 Sender History</div>', unsafe_allow_html=True)
            sender_history = result["details"]["sender_history"]
            if sender_history["seen_before"]:
                st.markdown(
                    f'<span style="color:var(--safe); font-size:12.5px;">✓ Known sender — you\'ve received {sender_history["previous_count"]} previous email(s) from this address.</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<span style="color:var(--pink); font-size:12.5px;">⚠ First time this sender has emailed you.</span>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pg-panel-label">💡 Why This Email Was Flagged</div>', unsafe_allow_html=True)
        st.markdown(f'<p class="explain-box">{explanation}</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pg-panel-label">✅ Recommended Action</div>', unsafe_allow_html=True)
        if score >= 70:
            rec = ("Do not click any links, scan any QR codes, or reply. Verify this "
                   "request through another channel — call the person using a number "
                   "you already have on file, not one provided in this email.")
            rc = "var(--red)"
        elif score >= 40:
            rec = "Treat with caution. Verify the sender's identity independently before acting."
            rc = "var(--pink)"
        elif score > 0:
            rec = "Minor red flags present. Stay alert, but no immediate action required."
            rc = "var(--pink)"
        else:
            rec = "No major red flags detected in this email."
            rc = "var(--safe)"
        st.markdown(
            f'<div class="rec-box" style="border-color:{rc}; background:{colors["dim"]}; color:var(--text-primary);">{rec}</div>',
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="pg-footer">
        <span>PHISHGUARD AI · LEARNING &amp; PORTFOLIO PROJECT</span>
        <span>NOT PRODUCTION SECURITY SOFTWARE — VERIFY SUSPICIOUS REQUESTS INDEPENDENTLY</span>
    </div>
    """,
    unsafe_allow_html=True,
)
