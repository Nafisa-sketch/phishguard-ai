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

from src import parser, detector, database, qr_detector
from src.features import psychology_scores

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


if __name__ == "__main__":
    app.run(debug=False, port=5000)
