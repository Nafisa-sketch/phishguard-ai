"""
threat_feed.py

Fetches REAL, live threat intelligence from URLhaus (abuse.ch) -- a
free, no-API-key-required public feed of recently reported malicious
URLs, run by a nonprofit Swiss security research group. This is used
by the Threat Intelligence page.

HONEST NOTE: this is a global feed of malware/phishing URLs reported
by security researchers worldwide -- it is NOT specific to your own
inbox or organization. It's included to show what a real threat-intel
integration looks like, not because these particular URLs targeted you.
"""

import csv
import io
import requests

URLHAUS_RECENT_FEED = "https://urlhaus.abuse.ch/downloads/csv_recent/"


def get_recent_threats(limit: int = 15) -> list:
    """
    Downloads the most recently reported malicious URLs from URLhaus.
    Returns [] on any failure (offline, feed down, etc) rather than
    raising -- the frontend should handle an empty list gracefully,
    not crash the page.
    """
    try:
        resp = requests.get(URLHAUS_RECENT_FEED, timeout=6)
        resp.raise_for_status()
    except Exception:
        return []

    lines = [line for line in resp.text.splitlines() if not line.startswith("#")]
    reader = csv.reader(lines)

    threats = []
    for row in reader:
        if len(row) < 6:
            continue
        threats.append({
            "date_added": row[1].strip('"'),
            "url": row[2].strip('"'),
            "threat_type": row[4].strip('"'),
            "tags": row[6].strip('"') if len(row) > 6 else "",
        })
        if len(threats) >= limit:
            break

    return threats
