"""
database.py

Stores every scan result in a local SQLite database (phishguard.db)
so the dashboard can show history, trends, and stats instead of
re-analyzing emails every time. SQLite needs no separate server --
it's just a file, which keeps this simple to run for a student project.
"""

import sqlite3
import json
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "processed", "phishguard.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scanned_at TEXT NOT NULL,
            sender TEXT,
            subject TEXT,
            risk_score INTEGER,
            threat_level TEXT,
            attack_type TEXT,
            techniques TEXT,
            explanation TEXT,
            latitude REAL,
            longitude REAL,
            location_label TEXT,
            psychology TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_scan(parsed: dict, result: dict, explanation: str, location: dict = None, psychology: dict = None) -> int:
    """Saves one scan result. Returns the new row's id."""
    conn = _connect()
    cur = conn.execute(
        """
        INSERT INTO scans (scanned_at, sender, subject, risk_score, threat_level,
                            attack_type, techniques, explanation, latitude, longitude, location_label, psychology)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(),
            parsed.get("sender"),
            parsed.get("subject"),
            result["risk_score"],
            result["threat_level"],
            result["attack_type"],
            json.dumps(result["techniques_detected"]),
            explanation,
            (location or {}).get("lat"),
            (location or {}).get("lon"),
            (location or {}).get("label"),
            json.dumps(psychology or {}),
        ),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_all_scans(limit: int = 200) -> list:
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM scans ORDER BY scanned_at DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_stats() -> dict:
    """Aggregate counts used by the Overview page stat cards."""
    conn = _connect()
    total = conn.execute("SELECT COUNT(*) c FROM scans").fetchone()["c"]
    safe = conn.execute("SELECT COUNT(*) c FROM scans WHERE threat_level='MINIMAL'").fetchone()["c"]
    suspicious = conn.execute("SELECT COUNT(*) c FROM scans WHERE threat_level IN ('LOW','MEDIUM')").fetchone()["c"]
    malicious = conn.execute("SELECT COUNT(*) c FROM scans WHERE threat_level='HIGH'").fetchone()["c"]
    avg_score = conn.execute("SELECT AVG(risk_score) a FROM scans").fetchone()["a"] or 0
    conn.close()
    return {
        "total": total,
        "safe": safe,
        "suspicious": suspicious,
        "malicious": malicious,
        "trust_score": round(100 - avg_score) if total else 100,
    }


def get_daily_trend(days: int = 7) -> list:
    """Returns per-day counts of safe/suspicious/malicious scans for the trend chart."""
    conn = _connect()
    rows = conn.execute(
        """
        SELECT substr(scanned_at, 1, 10) as day,
               SUM(CASE WHEN threat_level='MINIMAL' THEN 1 ELSE 0 END) as safe,
               SUM(CASE WHEN threat_level IN ('LOW','MEDIUM') THEN 1 ELSE 0 END) as suspicious,
               SUM(CASE WHEN threat_level='HIGH' THEN 1 ELSE 0 END) as malicious
        FROM scans
        GROUP BY day
        ORDER BY day DESC
        LIMIT ?
        """,
        (days,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in reversed(rows)]


def has_seen_sender_before(sender: str) -> dict:
    """
    Checks scan history for this sender. Used for the 'first-time sender'
    signal -- inspired by the research finding that comparing a message
    against a user's own historical senders reduces false positives
    (a brand-new sender asking for something unusual is more suspicious
    than a sender you've corresponded with many times before).
    """
    if not sender:
        return {"seen_before": False, "previous_count": 0}

    conn = _connect()
    row = conn.execute(
        "SELECT COUNT(*) c FROM scans WHERE sender = ?", (sender,)
    ).fetchone()
    conn.close()
    count = row["c"] if row else 0
    return {"seen_before": count > 0, "previous_count": count}


if __name__ == "__main__":
    init_db()
    print("Database initialized at:", DB_PATH)
