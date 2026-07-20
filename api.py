"""
api.py

A small Flask API that exposes our existing detection engine (parser,
detector, database) over HTTP, so the React frontend can call it.

This is the "backend server" -- run it separately from the React
frontend. It doesn't duplicate any detection logic; it just wraps the
existing src/ modules in HTTP endpoints.

Run with:
    python api.py
Runs on http://localhost:5000 by default.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from src import parser, detector, database, qr_detector, threat_feed
from src.features import psychology_scores, check_links

import anthropic

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

app = Flask(__name__)
CORS(app)  # allow the React dev server (different port) to call this API

database.init_db()


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Body (JSON): { "email_text": "...", "claimed_org": "..." (optional) }
    Returns the full detection result as JSON.
    """
    data = request.get_json(force=True)
    email_text = data.get("email_text", "")
    claimed_org = data.get("claimed_org") or None

    if not email_text.strip():
        return jsonify({"error": "email_text is required"}), 400

    parsed = parser.parse_raw_text(email_text)
    result = detector.analyze_email(parsed, claimed_org=claimed_org, raw_email_text=email_text)
    explanation = detector.build_explanation(result)
    psychology = psychology_scores(parsed.get("body") or "")
    database.save_scan(parsed, result, explanation, psychology=psychology)

    return jsonify({
        "parsed": parsed,
        "result": result,
        "explanation": explanation,
        "psychology": psychology,
    })


@app.route("/api/scan-qr", methods=["POST"])
def scan_qr():
    """
    Body: multipart/form-data with a file field named 'image'.
    Returns any QR codes found and what they decode to.
    """
    if "image" not in request.files:
        return jsonify({"error": "image file is required"}), 400

    file = request.files["image"]
    image_bytes = file.read()
    findings = qr_detector.scan_images_for_qr([
        {"filename": file.filename, "content_type": file.content_type, "data": image_bytes}
    ])
    return jsonify({"findings": findings})


@app.route("/api/history", methods=["GET"])
def history():
    limit = int(request.args.get("limit", 50))
    scans = database.get_all_scans(limit=limit)
    return jsonify({"scans": scans})


@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify(database.get_stats())


@app.route("/api/trend", methods=["GET"])
def trend():
    days = int(request.args.get("days", 7))
    return jsonify({"trend": database.get_daily_trend(days)})


@app.route("/api/senders", methods=["GET"])
def senders():
    return jsonify({"senders": database.get_sender_intelligence()})


@app.route("/api/attack-stories", methods=["GET"])
def attack_stories():
    min_score = int(request.args.get("min_score", 60))
    return jsonify({"stories": database.get_attack_stories(min_score=min_score)})


@app.route("/api/check-url", methods=["POST"])
def check_url():
    """Body: { "url": "..." } -- runs our existing link-reputation checks on a single URL."""
    data = request.get_json(force=True)
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "url is required"}), 400

    result = check_links([url])
    return jsonify({
        "url": url,
        "suspicious": result["suspicious_links_found"],
        "flagged_as": result["suspicious_links"],
    })


@app.route("/api/threat-feed", methods=["GET"])
def threat_feed_route():
    limit = int(request.args.get("limit", 15))
    return jsonify({"threats": threat_feed.get_recent_threats(limit=limit)})


@app.route("/api/integrations/status", methods=["GET"])
def integrations_status():
    gmail_connected = os.path.exists("credentials.json")
    gmail_authorized = os.path.exists("token.pickle")
    return jsonify({
        "gmail": {
            "credentials_found": gmail_connected,
            "authorized": gmail_authorized,
            "status": "connected" if gmail_authorized else ("credentials_only" if gmail_connected else "not_configured"),
        }
    })


@app.route("/api/model-info", methods=["GET"])
def model_info():
    """Reads the trained model's real evaluation metrics, if a model has been trained."""
    metrics_path = os.path.join("models", "metrics.txt")
    if not os.path.exists(metrics_path):
        return jsonify({"trained": False})

    with open(metrics_path) as f:
        content = f.read()

    import re
    accuracy_match = re.search(r"Accuracy:\s*([\d.]+)", content)
    precision_match = re.search(r"Precision:\s*([\d.]+)", content)
    recall_match = re.search(r"Recall:\s*([\d.]+)", content)
    f1_match = re.search(r"F1 Score:\s*([\d.]+)", content)
    train_size_match = re.search(r"Train size:\s*(\d+)", content)

    return jsonify({
        "trained": True,
        "accuracy": float(accuracy_match.group(1)) if accuracy_match else None,
        "precision": float(precision_match.group(1)) if precision_match else None,
        "recall": float(recall_match.group(1)) if recall_match else None,
        "f1_score": float(f1_match.group(1)) if f1_match else None,
        "train_size": int(train_size_match.group(1)) if train_size_match else None,
    })


@app.route("/api/copilot/chat", methods=["POST"])
def copilot_chat():
    """
    Body: { "message": "...", "history": [{"role": "user"/"assistant", "content": "..."}] }

    Calls the real Anthropic API, grounded with a short summary of the
    user's actual scan history so it can answer questions like "what's
    my riskiest sender" with real data, not made-up answers.
    """
    if not ANTHROPIC_API_KEY:
        return jsonify({
            "error": "not_configured",
            "message": "AI Copilot isn't configured yet. Set the ANTHROPIC_API_KEY environment variable and restart the backend to enable it.",
        }), 503

    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    history = data.get("history", [])

    if not user_message:
        return jsonify({"error": "message is required"}), 400

    # Ground the assistant in real data instead of letting it guess
    stats = database.get_stats()
    recent = database.get_all_scans(limit=10)
    senders = database.get_sender_intelligence()[:5]

    context = f"""Current PhishGuard AI dashboard data for this user:
- Total emails scanned: {stats['total']}
- Safe: {stats['safe']}, Suspicious: {stats['suspicious']}, Malicious: {stats['malicious']}
- Overall trust score: {stats['trust_score']}%

Most recent scans:
{chr(10).join(f"- {s['sender']}: {s['attack_type']} (risk {s['risk_score']}/100)" for s in recent[:5]) if recent else "No scans yet."}

Riskiest senders on file:
{chr(10).join(f"- {s['sender']}: max risk {s['max_risk']}, {s['email_count']} email(s)" for s in senders) if senders else "No sender data yet."}
"""

    system_prompt = (
        "You are the AI Copilot inside PhishGuard AI, an email threat detection dashboard. "
        "Answer questions about phishing, email security, and the user's own scan data below. "
        "Be concise (2-4 sentences typically). If asked about specific emails/senders, use the "
        "real data provided -- don't invent details not in the data.\n\n" + context
    )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        messages = history + [{"role": "user", "content": user_message}]
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=500,
            system=system_prompt,
            messages=messages,
        )
        reply_text = "".join(block.text for block in response.content if hasattr(block, "text"))
        return jsonify({"reply": reply_text})
    except Exception as e:
        return jsonify({"error": "api_error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)
