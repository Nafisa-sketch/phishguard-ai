"""
email_auth.py

Checks SPF, DKIM, and DMARC authentication results -- the same
industry-standard protocols Gmail/Outlook use to catch spoofed senders.

IMPORTANT LIMITATION (read before treating this as reliable):
These results only exist in a REAL email's headers -- the ones your
mail server adds when it receives a message. Plain pasted email text
(copied out of a webmail body) almost never includes them. This check
is only meaningful when analyzing an uploaded .eml file that still has
its full original headers intact.

When no authentication headers are found, this returns "NONE" (not
"FAIL") -- we can't penalize an email for missing information we were
never given.
"""

import re


def check_authentication(raw_email_text: str) -> dict:
    """
    Looks for SPF/DKIM/DMARC results in the raw email headers.
    Returns a dict with each protocol's result: 'pass', 'fail', or
    'none' (not found / not applicable).
    """
    if not raw_email_text:
        return _empty_result()

    # Modern mail servers usually combine all three into one header:
    # Authentication-Results: mx.google.com;
    #   spf=pass smtp.mailfrom=example.com;
    #   dkim=pass header.i=@example.com;
    #   dmarc=pass header.from=example.com
    auth_results_match = re.search(r"Authentication-Results:.*?(?=\n\S|\Z)", raw_email_text, re.IGNORECASE | re.DOTALL)

    spf = _extract_result(auth_results_match, "spf") if auth_results_match else None
    dkim = _extract_result(auth_results_match, "dkim") if auth_results_match else None
    dmarc = _extract_result(auth_results_match, "dmarc") if auth_results_match else None

    # Fallback: some servers write a standalone "Received-SPF:" header
    if spf is None:
        spf_line = re.search(r"Received-SPF:\s*(\w+)", raw_email_text, re.IGNORECASE)
        if spf_line:
            spf = spf_line.group(1).lower()

    return {
        "spf": spf or "none",
        "dkim": dkim or "none",
        "dmarc": dmarc or "none",
        "headers_found": auth_results_match is not None or spf is not None,
    }


def _extract_result(match, protocol: str) -> str:
    if not match:
        return None
    text = match.group(0)
    result = re.search(rf"{protocol}=(\w+)", text, re.IGNORECASE)
    return result.group(1).lower() if result else None


def _empty_result() -> dict:
    return {"spf": "none", "dkim": "none", "dmarc": "none", "headers_found": False}


def authentication_risk_signal(auth: dict) -> dict:
    """
    Turns the raw SPF/DKIM/DMARC results into a simple risk signal
    the detector can score. Only flags a real problem when we actually
    HAVE header data and it explicitly failed -- never penalizes an
    email just because headers were missing (that's the common case
    for pasted text, not evidence of anything).
    """
    if not auth["headers_found"]:
        return {"auth_checked": False, "auth_failed": False, "summary": "No authentication headers available to check (common for pasted email text)."}

    failed = auth["spf"] == "fail" or auth["dkim"] == "fail" or auth["dmarc"] == "fail"
    if failed:
        failed_protocols = [p for p in ("spf", "dkim", "dmarc") if auth[p] == "fail"]
        return {
            "auth_checked": True,
            "auth_failed": True,
            "summary": f"Authentication failed: {', '.join(p.upper() for p in failed_protocols)}. "
                       f"This is a strong signal the sender address was spoofed.",
        }

    return {"auth_checked": True, "auth_failed": False, "summary": "SPF/DKIM/DMARC checks passed."}


if __name__ == "__main__":
    sample = """Delivered-To: you@yourcompany.com
Authentication-Results: mx.google.com;
       spf=fail smtp.mailfrom=attacker.com;
       dkim=none;
       dmarc=fail header.from=company.com
From: ceo.company@gmail.com
Subject: Urgent

Body text here.
"""
    result = check_authentication(sample)
    print("Auth result:", result)
    print("Risk signal:", authentication_risk_signal(result))
