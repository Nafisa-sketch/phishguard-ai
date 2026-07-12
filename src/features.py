"""
features.py

Looks at a parsed email and pulls out specific "clues" (features) that
indicate phishing / spear phishing / BEC. Each function checks one
type of clue and returns a simple result. detector.py will combine
all of these into a final risk score.
"""

import re
import tldextract


# Words that create pressure / urgency -- a classic social engineering tactic
URGENCY_WORDS = [
    "urgent", "immediately", "asap", "right away", "as soon as possible",
    "act now", "final notice", "expire", "expires", "expiring",
    "before 5 pm", "today only", "last chance", "verify your account",
    "suspended", "locked", "limited time",
]

# Words/phrases that invoke authority -- another classic tactic
AUTHORITY_WORDS = [
    "ceo", "cfo", "president", "director", "hr department",
    "it department", "finance department", "management",
    "as requested by", "on behalf of", "official notice",
]

# Phrases that signal a request for money, credentials, or sensitive data
REQUEST_WORDS = [
    "wire transfer", "bank details", "gift card", "payment",
    "password", "login", "verify your account", "confirm your identity",
    "click here", "reset your password", "account number",
    "social security", "invoice", "attached invoice",
]

# Free email providers real companies/executives don't normally send from
FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "aol.com", "icloud.com", "protonmail.com",
]


def check_urgency(body: str) -> dict:
    body_lower = body.lower()
    found = [w for w in URGENCY_WORDS if w in body_lower]
    return {"urgency_detected": len(found) > 0, "urgency_phrases": found}


def check_authority(body: str) -> dict:
    body_lower = body.lower()
    found = [w for w in AUTHORITY_WORDS if w in body_lower]
    return {"authority_detected": len(found) > 0, "authority_phrases": found}


def check_request_type(body: str) -> dict:
    body_lower = body.lower()
    found = [w for w in REQUEST_WORDS if w in body_lower]
    return {"request_detected": len(found) > 0, "request_phrases": found}


def check_sender_domain(sender: str, claimed_org: str = None) -> dict:
    """
    Looks at the sender's email address and flags common red flags:
    - sending from a free email provider while claiming to be a company/exec
    - the domain not matching the organization the person claims to represent
    """
    if not sender:
        return {"domain_suspicious": False, "reason": None}

    email_match = re.search(r"[\w\.-]+@[\w\.-]+", sender)
    if not email_match:
        return {"domain_suspicious": False, "reason": None}

    email_address = email_match.group(0)
    domain = email_address.split("@")[-1].lower()

    if domain in FREE_EMAIL_DOMAINS:
        return {
            "domain_suspicious": True,
            "reason": f"Sender uses a free email provider ({domain}), "
                      f"which is unusual for an official company/executive email.",
        }

    if claimed_org:
        extracted = tldextract.extract(domain)
        if claimed_org.lower() not in extracted.domain.lower():
            return {
                "domain_suspicious": True,
                "reason": f"Sender domain '{domain}' does not match the "
                          f"claimed organization '{claimed_org}'.",
            }

    return {"domain_suspicious": False, "reason": None}


def check_links(links: list) -> dict:
    """
    Basic link red flags: IP-address links, excessive subdomains,
    lookalike domains (very basic version -- can be upgraded later
    with a real domain-reputation API).
    """
    suspicious_links = []
    for link in links:
        extracted = tldextract.extract(link)
        domain = extracted.domain
        subdomain = extracted.subdomain

        is_ip = bool(re.match(r"https?://\d+\.\d+\.\d+\.\d+", link))
        many_subdomains = subdomain.count(".") >= 2

        if is_ip or many_subdomains:
            suspicious_links.append(link)

    return {
        "suspicious_links_found": len(suspicious_links) > 0,
        "suspicious_links": suspicious_links,
    }


def extract_all_features(parsed_email: dict, claimed_org: str = None) -> dict:
    """
    Runs every check above and returns one combined dictionary.
    This is the single function detector.py will call.
    """
    body = parsed_email.get("body") or ""
    sender = parsed_email.get("sender") or ""
    links = parsed_email.get("links") or []

    return {
        **check_urgency(body),
        **check_authority(body),
        **check_request_type(body),
        **check_sender_domain(sender, claimed_org),
        **check_links(links),
    }


if __name__ == "__main__":
    sample_email = {
        "sender": "ceo.company@gmail.com",
        "subject": "Urgent wire transfer needed",
        "body": "Hi Sarah, as requested by the Finance Department, please "
                "wire transfer $5,000 immediately before 5 PM today.",
        "links": ["http://192.168.1.1/login"],
    }

    features = extract_all_features(sample_email, claimed_org="company")
    for key, value in features.items():
        print(f"{key}: {value}")
