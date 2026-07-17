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

# Senior-executive-specific titles -- used to distinguish "whaling"
# (an attack specifically impersonating a top executive) from generic
# spear phishing/BEC that might impersonate a mid-level manager.
EXECUTIVE_TITLES = [
    "ceo", "chief executive officer", "cfo", "chief financial officer",
    "coo", "chief operating officer", "president", "founder", "chairman",
]

# Phrases that ask the reader to call a number -- classic "callback
# phishing" pattern, where the malicious action happens over a phone
# call instead of a link click.
CALLBACK_PHRASES = [
    "call us at", "call the number below", "call this number",
    "verify by calling", "contact us at", "reach us at",
    "call immediately", "please call", "call to confirm",
]

# Curiosity-based manipulation: makes the reader want to "see" something
CURIOSITY_WORDS = [
    "you won't believe", "see who viewed", "someone shared", "check this out",
    "you have been selected", "important update about you", "look what happened",
    "guess what", "shocking",
]

# Greed-based manipulation: promises money, prizes, rewards
GREED_WORDS = [
    "you have won", "claim your prize", "free gift", "cash reward",
    "lottery", "refund pending", "bonus payment", "exclusive offer",
    "act now to claim",
]

# Device Code / OAuth authorization-flow phishing: the attacker abuses a
# REAL Microsoft/Google/GitHub device-login flow. The victim visits the
# genuine login page and enters a code the attacker generated, which
# hands the attacker a valid access token -- no password is stolen, no
# fake page is used, so traditional URL-reputation checks miss this
# entirely. Documented in real 2024-2025 campaigns (e.g. Storm-2372).
DEVICE_CODE_DOMAINS = [
    "aka.ms/devicelogin", "microsoft.com/devicelogin",
    "login.microsoftonline.com/common/oauth2/deviceauth",
    "github.com/login/device", "google.com/device",
]

DEVICE_CODE_PHRASES = [
    "enter the code", "enter this code", "device code", "enter code to sign in",
    "go to aka.ms", "authenticate this device", "sign in on your other device",
    "enter code", "verify device", "device verification", "authorize this device",
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

# Well-established legitimate service domains. If a sender's domain (or
# a subdomain of it) matches one of these, we trust it much more
# heavily -- these are large organizations that send millions of
# legitimate transactional emails (login links, password resets, job
# notifications) that would otherwise look "urgent" or "request-like"
# to a pure keyword scan.
#
# HONEST LIMITATION: this list is small and manually curated. A
# company not on this list isn't treated as suspicious -- it's just
# not given the extra trust boost. This reduces false positives for
# common cases; it does not, and cannot, guarantee 100% accuracy.
# No detector, rule-based or ML, can promise that.
TRUSTED_DOMAINS = [
    "google.com", "microsoft.com", "apple.com", "amazon.com", "anthropic.com",
    "indeed.com", "linkedin.com", "github.com", "successfactors.com", "successfactors.eu",
    "jobs2web.com", "workday.com", "salesforce.com", "dropbox.com", "slack.com",
    "zoom.us", "dlr.de", "fraunhofer.de",
]

# Brand names that are common spoofing targets. If the sender's DISPLAY
# NAME claims to be one of these brands but the actual email domain
# doesn't match, that's classic "display name spoofing" --
# e.g. "PayPal Support <random123@gmail.com>".
SPOOFABLE_BRANDS = {
    "paypal": "paypal.com", "microsoft": "microsoft.com", "apple": "apple.com",
    "amazon": "amazon.com", "google": "google.com", "netflix": "netflix.com",
    "bank of america": "bankofamerica.com", "chase": "chase.com", "wells fargo": "wellsfargo.com",
    "dhl": "dhl.com", "fedex": "fedex.com", "ups": "ups.com",
}


def check_urgency(body: str) -> dict:
    body_lower = body.lower()
    found = [w for w in URGENCY_WORDS if w in body_lower]
    return {"urgency_detected": len(found) > 0, "urgency_phrases": found}


def check_authority(body: str) -> dict:
    body_lower = body.lower()
    found = [w for w in AUTHORITY_WORDS if w in body_lower]
    return {"authority_detected": len(found) > 0, "authority_phrases": found}


def check_executive_impersonation(body: str) -> dict:
    """
    Specifically checks for impersonation of a senior executive (CEO,
    CFO, President, etc). This is what distinguishes 'whaling' from a
    generic spear phishing / BEC attempt that might impersonate a
    mid-level manager instead.
    """
    body_lower = body.lower()
    found = [w for w in EXECUTIVE_TITLES if w in body_lower]
    return {"executive_impersonation_detected": len(found) > 0, "executive_titles_found": found}


def check_callback_phishing(body: str) -> dict:
    """
    Looks for the 'callback phishing' pattern: a phone number paired
    with language urging the reader to call it. The attack happens
    over the phone call itself, not a link click.
    """
    body_lower = body.lower()
    has_callback_phrase = any(phrase in body_lower for phrase in CALLBACK_PHRASES)

    # Matches common phone number formats, e.g. +1-800-555-0123, (800) 555 0123, 800.555.0123
    phone_pattern = r"(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}"
    phone_matches = re.findall(phone_pattern, body)
    has_phone_number = len(phone_matches) > 0

    return {
        "callback_detected": has_callback_phrase and has_phone_number,
        "callback_phrase_found": has_callback_phrase,
        "phone_number_found": has_phone_number,
    }


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
        # Don't flag a "mismatch" for well-known legitimate services --
        # a Google or Amazon notification email legitimately won't
        # contain the user's own company name in its domain.
        is_trusted = any(domain == d or domain.endswith("." + d) for d in TRUSTED_DOMAINS)
        extracted = tldextract.extract(domain)
        if not is_trusted and claimed_org.lower() not in extracted.domain.lower():
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


def check_device_code_phishing(body: str, links: list) -> dict:
    """
    Detects 'device code phishing' -- the attacker sends a REAL
    Microsoft/Google/GitHub device-authorization link and asks the
    victim to enter a code. The victim ends up on the genuine login
    page and unknowingly hands the attacker a valid access token.
    No password is stolen and no fake page is involved, which is why
    normal URL-reputation and fake-login-page checks miss it entirely.
    """
    body_lower = body.lower()
    all_links_text = " ".join(links).lower()

    domain_hit = any(d in body_lower or d in all_links_text for d in DEVICE_CODE_DOMAINS)
    phrase_hit = any(p in body_lower for p in DEVICE_CODE_PHRASES)

    return {
        "device_code_phishing_detected": domain_hit and phrase_hit,
        "device_code_domain_found": domain_hit,
    }


def psychology_scores(body: str) -> dict:
    """
    Computes a rough 0-100 score for each of the 5 classic social
    engineering manipulation levers, for the 'Psychological Manipulation'
    radar chart. This is a simple keyword-density heuristic, not a
    trained model -- it's meant to illustrate WHICH lever an email
    leans on, not to be a precise measurement.
    """
    body_lower = body.lower()

    def density_score(words):
        hits = sum(1 for w in words if w in body_lower)
        return min(100, hits * 35)  # each matched phrase is a strong signal

    return {
        "urgency": density_score(URGENCY_WORDS),
        "authority": density_score(AUTHORITY_WORDS),
        "curiosity": density_score(CURIOSITY_WORDS),
        "greed": density_score(GREED_WORDS),
        "fear": density_score(["suspended", "locked", "unauthorized access", "account closed", "legal action", "penalty"]),
    }


def check_trusted_domain(sender: str) -> dict:
    """
    Checks if the sender's domain (or a subdomain of it) matches our
    curated list of well-established legitimate services.
    """
    if not sender:
        return {"is_trusted_domain": False}

    email_match = re.search(r"[\w\.-]+@[\w\.-]+", sender)
    if not email_match:
        return {"is_trusted_domain": False}

    domain = email_match.group(0).split("@")[-1].lower()
    is_trusted = any(domain == d or domain.endswith("." + d) for d in TRUSTED_DOMAINS)
    return {"is_trusted_domain": is_trusted}


def check_display_name_spoofing(sender: str) -> dict:
    """
    Checks for a classic spoofing pattern: the display name claims to
    be a well-known brand, but the actual sending domain doesn't match
    that brand at all -- e.g. 'PayPal Security <alerts@random-xyz.com>'.
    """
    if not sender or "<" not in sender:
        return {"display_name_spoofing_detected": False, "claimed_brand": None}

    display_name = sender.split("<")[0].strip().strip('"').lower()
    email_match = re.search(r"[\w\.-]+@[\w\.-]+", sender)
    if not email_match:
        return {"display_name_spoofing_detected": False, "claimed_brand": None}

    domain = email_match.group(0).split("@")[-1].lower()

    for brand, real_domain in SPOOFABLE_BRANDS.items():
        if brand in display_name and not (domain == real_domain or domain.endswith("." + real_domain)):
            return {"display_name_spoofing_detected": True, "claimed_brand": brand}

    return {"display_name_spoofing_detected": False, "claimed_brand": None}


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
        **check_executive_impersonation(body),
        **check_callback_phishing(body),
        **check_device_code_phishing(body, links),
        **check_trusted_domain(sender),
        **check_display_name_spoofing(sender),
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
