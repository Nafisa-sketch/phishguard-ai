"""
scan_inbox.py

Run this to scan your real Gmail inbox: fetches recent emails,
analyzes each one with our existing detector, saves results to the
database, and prints a summary. The dashboard (Mission Control /
Reports) will then show these scans automatically.

Run with:
    python scan_inbox.py
    python scan_inbox.py --count 20    (scan more/fewer emails)
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.gmail_client import get_gmail_service, fetch_recent_messages, gmail_message_to_parsed
from src import detector, database
from src.features import psychology_scores

LEVEL_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟠", "LOW": "🟡", "MINIMAL": "🟢"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=10, help="How many recent emails to scan")
    args = parser.parse_args()

    database.init_db()

    print("Connecting to Gmail (a browser window may open for login)...")
    service = get_gmail_service()

    print(f"Fetching {args.count} recent emails...")
    messages = fetch_recent_messages(service, max_results=args.count)

    if not messages:
        print("No messages found in inbox.")
        return

    print(f"Scanning {len(messages)} emails...\n")

    for msg_ref in messages:
        parsed = gmail_message_to_parsed(service, msg_ref["id"])
        result = detector.analyze_email(parsed, raw_email_text=None)
        explanation = detector.build_explanation(result)
        psych = psychology_scores(parsed.get("body") or "")
        database.save_scan(parsed, result, explanation, psychology=psych)

        emoji = LEVEL_EMOJI.get(result["threat_level"], "⚪")
        subject = (parsed.get("subject") or "(no subject)")[:60]
        print(f"{emoji} [{result['risk_score']:3d}/100] {result['attack_type']:<35} | {subject}")

    print(f"\nDone. {len(messages)} emails scanned and saved.")
    print("Open the dashboard (Mission Control / Reports) to see the results.")


if __name__ == "__main__":
    main()
