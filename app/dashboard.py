"""
dashboard.py

Full PhishGuard AI dashboard: sidebar navigation, Overview page with
live stats pulled from a local database, a dedicated Email Analysis
page, a standalone QR Code Analyzer, and a Reports & Logs history
table. Styled in the violet/pink dark theme.

Run with:
    streamlit run app/dashboard.py

HONEST NOTE on the World Threat Map: sender location is approximated
from IP addresses found in email "Received" headers when available.
Most pasted emails (especially from webmail like Gmail) won't include
a usable IP, so many scans simply won't have a map point -- that's
expected, not a bug. See src/geolocation.py for details.
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import plotly.graph_objects as go

from src import parser, detector, database, geolocation
from src.features import psychology_scores

database.init_db()

st.set_page_config(
    page_title="PhishGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------
# THEME
# ----------------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

:root {
    --bg-deep: #0B0A14; --bg-panel: #14111F; --bg-panel-raised: #191530;
    --border: #241F38; --border-bright: #3D3560;
    --text-primary: #EDEBF7; --text-muted: #B3A9CC; --text-dim: #7C6FA8; --text-dimmer: #5C5480;
    --violet: #A78BFA; --violet-dim: rgba(167,139,250,0.12);
    --pink: #F472B6; --pink-dim: rgba(244,114,182,0.12);
    --red: #F0495C; --red-dim: rgba(240,73,92,0.12);
    --safe: #3ECF8E; --safe-dim: rgba(62,207,142,0.12);
    --amber: #F5B043; --amber-dim: rgba(245,176,67,0.12);
}
#MainMenu, footer, header {visibility: hidden;}
.stApp { background: radial-gradient(ellipse 800px 450px at 10% -10%, rgba(167,139,250,0.06), transparent), var(--bg-deep); }
.block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1300px; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--text-primary); }
section[data-testid="stSidebar"] { background: var(--bg-panel); border-right: 1px solid var(--border); }

.pg-panel { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px; padding: 18px 20px; margin-bottom: 14px; }
.pg-panel-label { font-family: 'JetBrains Mono', monospace; font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim); margin-bottom: 10px; }

.stat-card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; }
.stat-label { font-size: 12px; color: var(--text-muted); margin-bottom: 6px; }
.stat-value { font-family: 'Space Grotesk', sans-serif; font-size: 26px; font-weight: 700; color: var(--text-primary); }
.stat-sub { font-family: 'JetBrains Mono', monospace; font-size: 10.5px; color: var(--text-dim); margin-top: 4px; }

.chip { background: var(--bg-panel-raised); border: 1px solid var(--border-bright); border-radius: 8px; padding: 6px 12px; font-size: 12.5px; display: inline-block; margin: 3px 4px 3px 0; }
.feed-row { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 12.5px; }
.feed-row:last-child { border-bottom: none; }
.badge { font-family: 'JetBrains Mono', monospace; font-size: 9.5px; padding: 3px 9px; border-radius: 100px; border: 1px solid; font-weight: 600; }

.stTextArea textarea, .stTextInput input {
    background: var(--bg-panel-raised) !important; border: 1px solid var(--border) !important; border-radius: 8px !important;
    color: var(--text-primary) !important; font-family: 'JetBrains Mono', monospace !important; font-size: 13px !important;
}
.stButton button {
    background: linear-gradient(135deg, var(--violet), #8B6FE0) !important; color: #1A1030 !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-family: 'Space Grotesk', sans-serif !important;
}
.qr-panel { background: linear-gradient(135deg, var(--pink-dim), var(--bg-panel)); border: 1.5px solid var(--pink); border-radius: 12px; padding: 16px 18px; margin-bottom: 14px; }
.rec-box { border-radius: 10px; padding: 14px 16px; font-size: 13.5px; line-height: 1.6; border: 1px solid; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

LEVEL_COLORS = {
    "HIGH": {"main": "#F0495C", "dim": "rgba(240,73,92,0.12)"},
    "MEDIUM": {"main": "#F472B6", "dim": "rgba(244,114,182,0.12)"},
    "LOW": {"main": "#F5B043", "dim": "rgba(245,176,67,0.12)"},
    "MINIMAL": {"main": "#3ECF8E", "dim": "rgba(62,207,142,0.12)"},
}

# ----------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "Overview"

with st.sidebar:
    st.markdown("### 🛡️ PhishGuard AI")
    st.caption("AI Email & Threat Defense")
    st.write("")
    page = st.radio(
        "Navigate",
        ["Overview", "Email Analysis", "QR Code Analyzer", "Reports & Logs"],
        label_visibility="collapsed",
        index=["Overview", "Email Analysis", "QR Code Analyzer", "Reports & Logs"].index(st.session_state.page),
    )
    st.session_state.page = page
    st.write("")
    st.markdown("---")
    st.caption("PROTECTION STATUS")
    st.success("🟢 Real-time protection ON")
    st.markdown("---")
    st.caption("PhishGuard AI · Learning & Portfolio Project")

# ----------------------------------------------------------------------
# OVERVIEW PAGE
# ----------------------------------------------------------------------
if st.session_state.page == "Overview":
    st.markdown("## Good Morning 👋")
    st.caption("AI is actively protecting your inbox from email threats.")

    stats = database.get_stats()
    scans = database.get_all_scans(limit=50)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Trust Score</div><div class="stat-value">{stats["trust_score"]}%</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Emails Scanned</div><div class="stat-value">{stats["total"]}</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Safe Emails</div><div class="stat-value" style="color:#3ECF8E;">{stats["safe"]}</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-card"><div class="stat-label">Malicious Emails</div><div class="stat-value" style="color:#F0495C;">{stats["malicious"]}</div></div>', unsafe_allow_html=True)

    st.write("")

    if not scans:
        st.info("No scans yet. Go to **Email Analysis** to scan your first email — results will appear here automatically.")
    else:
        latest = scans[0]
        colors = LEVEL_COLORS.get(latest["threat_level"], LEVEL_COLORS["MINIMAL"])

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">Latest Email Analysis</div>', unsafe_allow_html=True)
            st.markdown(f"**From:** {latest['sender'] or 'Unknown'}")
            st.markdown(f"**Subject:** {latest['subject'] or '(no subject)'}")
            st.markdown(
                f'<div style="font-family:JetBrains Mono,monospace; font-size:34px; font-weight:700; color:{colors["main"]}; margin-top:8px;">{latest["risk_score"]}<span style="font-size:14px; color:var(--text-dimmer);">/100</span></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f'<span class="badge" style="color:{colors["main"]}; border-color:{colors["main"]}; background:{colors["dim"]};">{latest["threat_level"]} RISK</span>', unsafe_allow_html=True)
            st.markdown(f"**Attack Type:** {latest['attack_type']}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Psychology radar
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">Psychological Manipulation</div>', unsafe_allow_html=True)
            import json as _json
            psych = _json.loads(latest["psychology"]) if latest["psychology"] else {}
            if psych:
                categories = list(psych.keys())
                values = list(psych.values())
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values + [values[0]], theta=[c.capitalize() for c in categories] + [categories[0].capitalize()],
                    fill='toself', line=dict(color="#A78BFA"), fillcolor="rgba(167,139,250,0.25)",
                ))
                fig.update_layout(
                    polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=True, range=[0, 100], color="#5C5480", gridcolor="#241F38"),
                               angularaxis=dict(color="#EDEBF7", gridcolor="#241F38")),
                    showlegend=False, paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#EDEBF7"),
                    margin=dict(l=30, r=30, t=20, b=20), height=280,
                )
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            else:
                st.caption("No manipulation signals detected in the latest scan.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">Attack Techniques Detected</div>', unsafe_allow_html=True)
            import json as _json2
            techniques = _json2.loads(latest["techniques"]) if latest["techniques"] else []
            if techniques:
                for t in techniques:
                    st.markdown(f'<span class="chip">⚠️ {t}</span>', unsafe_allow_html=True)
            else:
                st.caption("No techniques flagged.")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">Live Threat Feed</div>', unsafe_allow_html=True)
            for s in scans[:6]:
                c = LEVEL_COLORS.get(s["threat_level"], LEVEL_COLORS["MINIMAL"])
                t_short = datetime.fromisoformat(s["scanned_at"]).strftime("%H:%M")
                st.markdown(
                    f'<div class="feed-row"><span>{t_short} · {s["attack_type"]}</span>'
                    f'<span class="badge" style="color:{c["main"]}; border-color:{c["main"]}; background:{c["dim"]};">{s["threat_level"]}</span></div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

    # Trend chart
    trend = database.get_daily_trend(7)
    if trend:
        st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pg-panel-label">Email Threat Trend (Last 7 Days)</div>', unsafe_allow_html=True)
        fig2 = go.Figure()
        days = [t["day"] for t in trend]
        fig2.add_trace(go.Scatter(x=days, y=[t["safe"] for t in trend], name="Safe", line=dict(color="#3ECF8E")))
        fig2.add_trace(go.Scatter(x=days, y=[t["suspicious"] for t in trend], name="Suspicious", line=dict(color="#F5B043")))
        fig2.add_trace(go.Scatter(x=days, y=[t["malicious"] for t in trend], name="Malicious", line=dict(color="#F0495C")))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#EDEBF7"),
            legend=dict(orientation="h", y=1.15), margin=dict(l=10, r=10, t=10, b=10), height=260,
            xaxis=dict(gridcolor="#241F38"), yaxis=dict(gridcolor="#241F38"),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # World map
    mapped_scans = [s for s in scans if s["latitude"] and s["longitude"]]
    st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pg-panel-label">World Threat Map (Approximate)</div>', unsafe_allow_html=True)
    st.caption(
        "⚠️ Sender location is best-effort, from IP addresses found in email headers when available. "
        "Most pasted emails won't include one — this map only plots scans where a location was found."
    )
    if mapped_scans:
        fig3 = go.Figure(go.Scattergeo(
            lat=[s["latitude"] for s in mapped_scans],
            lon=[s["longitude"] for s in mapped_scans],
            text=[s["location_label"] for s in mapped_scans],
            marker=dict(size=10, color=[LEVEL_COLORS.get(s["threat_level"], LEVEL_COLORS["MINIMAL"])["main"] for s in mapped_scans]),
        ))
        fig3.update_geos(bgcolor="rgba(0,0,0,0)", showland=True, landcolor="#191530", showocean=True, oceancolor="#0B0A14", showcountries=True, countrycolor="#241F38")
        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=0, b=0), height=320)
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No location data available yet for any scan.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
    st.markdown('<div class="pg-panel-label">Quick Actions</div>', unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3)
    if qa1.button("📧 Analyze Email", use_container_width=True):
        st.session_state.page = "Email Analysis"
        st.rerun()
    if qa2.button("▣ Scan QR Code", use_container_width=True):
        st.session_state.page = "QR Code Analyzer"
        st.rerun()
    if qa3.button("📋 View Logs", use_container_width=True):
        st.session_state.page = "Reports & Logs"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# EMAIL ANALYSIS PAGE
# ----------------------------------------------------------------------
elif st.session_state.page == "Email Analysis":
    st.markdown("## 📧 Email Analysis")
    st.caption("Paste a full email (including headers, if you have them) to scan it.")

    col_a, col_b = st.columns([2, 1])
    with col_a:
        email_text = st.text_area("Paste email", height=220, label_visibility="collapsed",
            placeholder="From: ceo.company@gmail.com\nSubject: Urgent wire transfer needed\n\nHi Sarah, please wire $5,000 immediately...")
    with col_b:
        claimed_org = st.text_input("Organization name (optional)")
        st.write("")
        run = st.button("Run Scan →", type="primary", use_container_width=True)

    if run and email_text.strip():
        parsed = parser.parse_raw_text(email_text)
        result = detector.analyze_email(parsed, claimed_org=claimed_org or None)
        explanation = detector.build_explanation(result)
        psych = psychology_scores(parsed.get("body") or "")
        location = geolocation.get_scan_location(email_text)
        database.save_scan(parsed, result, explanation, location, psych)

        colors = LEVEL_COLORS.get(result["threat_level"], LEVEL_COLORS["MINIMAL"])
        qr_signal = result["details"]["qr_signal"]

        st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pg-panel-label">Uploaded Email</div>', unsafe_allow_html=True)
        st.markdown(f"**From:** {parsed.get('sender') or 'Unknown'}  \n**Subject:** {parsed.get('subject') or '(no subject)'}")
        st.text_area("Body", value=(parsed.get("body") or "").strip(), height=100, disabled=True, label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

        if qr_signal["qr_detected"]:
            st.markdown('<div class="qr-panel">', unsafe_allow_html=True)
            st.markdown("**▣ QR Code Threat Detected · Quishing**")
            st.write(qr_signal["risk_note"])
            for url in qr_signal.get("qr_urls", []):
                st.code(url, language=None)
            st.markdown('</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">Risk Score</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-family:JetBrains Mono,monospace; font-size:36px; font-weight:700; color:{colors["main"]}">{result["risk_score"]}/100</div>', unsafe_allow_html=True)
            st.markdown(f'<span class="badge" style="color:{colors["main"]}; border-color:{colors["main"]}; background:{colors["dim"]};">{result["threat_level"]} RISK</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
            st.markdown('<div class="pg-panel-label">Attack Category</div>', unsafe_allow_html=True)
            st.markdown(f"### {result['attack_type']}")
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pg-panel-label">Objects Detected</div>', unsafe_allow_html=True)
        for t in result["techniques_detected"]:
            st.markdown(f'<span class="chip">⚠️ {t}</span>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pg-panel-label">Why This Email Was Flagged</div>', unsafe_allow_html=True)
        st.write(explanation)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="pg-panel">', unsafe_allow_html=True)
        st.markdown('<div class="pg-panel-label">Recommended Action</div>', unsafe_allow_html=True)
        score = result["risk_score"]
        if score >= 70:
            rec = "Do not click links or scan QR codes. Verify through another channel before acting."
        elif score >= 40:
            rec = "Treat with caution. Verify the sender independently."
        elif score > 0:
            rec = "Minor red flags. Stay alert."
        else:
            rec = "No major red flags detected."
        st.markdown(f'<div class="rec-box" style="border-color:{colors["main"]}; background:{colors["dim"]};">{rec}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.success("Saved to Reports & Logs.")
    elif run:
        st.warning("Paste an email first.")

# ----------------------------------------------------------------------
# QR CODE ANALYZER PAGE (standalone -- upload just an image)
# ----------------------------------------------------------------------
elif st.session_state.page == "QR Code Analyzer":
    st.markdown("## ▣ QR Code Analyzer")
    st.caption("Upload a QR code image directly (e.g. a screenshot from an email) to check where it leads.")

    uploaded = st.file_uploader("Upload QR image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded:
        from src import qr_detector
        image_bytes = uploaded.read()
        findings = qr_detector.scan_images_for_qr([{"filename": uploaded.name, "content_type": "image/*", "data": image_bytes}])
        st.image(image_bytes, width=200)

        if findings:
            for f in findings:
                st.markdown('<div class="qr-panel">', unsafe_allow_html=True)
                st.markdown(f"**Decoded content:**")
                st.code(f["qr_content"], language=None)
                if f["is_url"]:
                    st.warning("This QR code points to a URL. Verify it's legitimate before visiting — never scan QR codes from unsolicited emails.")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No QR code detected in this image.")

# ----------------------------------------------------------------------
# REPORTS & LOGS PAGE
# ----------------------------------------------------------------------
elif st.session_state.page == "Reports & Logs":
    st.markdown("## 📋 Reports & Logs")
    st.caption("Full history of every email scanned.")

    scans = database.get_all_scans(limit=500)
    if not scans:
        st.info("No scans yet.")
    else:
        import pandas as pd
        df = pd.DataFrame(scans)[["scanned_at", "sender", "subject", "risk_score", "threat_level", "attack_type"]]
        df.columns = ["Scanned At", "Sender", "Subject", "Risk Score", "Threat Level", "Attack Type"]
        st.dataframe(df, use_container_width=True, height=500)
