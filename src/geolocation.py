"""
geolocation.py

Best-effort location lookup for the "World Threat Map" panel.

HONEST NOTE (important -- read this before treating the map as accurate):
Email "From" addresses can be spoofed, and consumer email (Gmail, etc.)
doesn't expose the sender's real IP to us at all. The only IP we can
sometimes recover is from the email's "Received" headers, which shows
mail-server hops, not necessarily the attacker's real location. Real
enterprise security tools spend serious money on threat-intelligence
feeds to do this accurately.

This module does a best-effort lookup when an IP is available, and
CLEARLY labels results as "approximate" in the UI. When no IP can be
found (the common case, especially for pasted email text), it returns
None -- the dashboard should skip plotting that scan rather than
inventing a fake location.
"""

import re
import requests


def extract_ip_from_headers(raw_email_text: str) -> str:
    """
    Looks for an IP address inside 'Received:' header lines, which is
    the closest thing to a sender IP available in plain email text.
    Returns the first plausible public-looking IP found, or None.
    """
    if not raw_email_text:
        return None

    received_lines = re.findall(r"Received:.*", raw_email_text, re.IGNORECASE)
    ip_pattern = r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b"

    for line in received_lines:
        matches = re.findall(ip_pattern, line)
        for ip in matches:
            if not _is_private_ip(ip):
                return ip
    return None


def _is_private_ip(ip: str) -> bool:
    parts = ip.split(".")
    if len(parts) != 4:
        return True
    first = int(parts[0])
    second = int(parts[1])
    return (
        first == 10
        or (first == 172 and 16 <= second <= 31)
        or (first == 192 and second == 168)
        or first == 127
    )


def lookup_ip_location(ip: str) -> dict:
    """
    Looks up an approximate city-level location for an IP using a free
    public API (ip-api.com). Requires internet access. Returns None on
    any failure -- callers should treat that as "location unavailable",
    not plot a wrong/fake point.
    """
    if not ip:
        return None
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = resp.json()
        if data.get("status") == "success":
            return {
                "lat": data["lat"],
                "lon": data["lon"],
                "label": f"{data.get('city', 'Unknown')}, {data.get('country', '')}",
            }
    except Exception:
        pass
    return None


def get_scan_location(raw_email_text: str) -> dict:
    """
    Main entry point: tries to find a real, approximate location from
    the email's headers. Returns None if it can't -- the dashboard
    should handle that by simply not plotting a point for this scan,
    rather than faking a location.
    """
    ip = extract_ip_from_headers(raw_email_text)
    if not ip:
        return None
    return lookup_ip_location(ip)
