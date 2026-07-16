"""
detector.py

Combines everything (text features + QR code findings) into one final
result: a risk score, a threat classification, and the list of specific
techniques detected. This is the "brain" that ties parser.py,
features.py, and qr_detector.py together.
"""

from src import features as feat
from src import qr_detector
from src import email_auth
from src import database


# How many points each detected signal adds toward the risk score.
# Total is capped at 100.
WEIGHTS = {
    "urgency": 20,
    "authority": 20,
    "request": 20,
    "domain_suspicious": 25,
    "suspicious_links": 20,
    "qr_detected": 25,
    "callback": 15,
    "auth_failed": 30,
    "new_sender": 10,
    "device_code": 35,
}


def analyze_email(parsed_email: dict, claimed_org: str = None, raw_email_text: str = None) -> dict:
    """
    Takes a parsed email (from parser.py) and returns the full
    detection result: risk score, threat level, techniques found,
    and which signals contributed.

    raw_email_text (optional): the original, unparsed email text/bytes
    as a string. Only needed for the SPF/DKIM/DMARC authentication
    check, since that data lives in raw headers that parser.py doesn't
    keep. Pass this when analyzing an uploaded .eml file; for plain
    pasted text it's fine to leave it out (there are usually no
    authentication headers to find anyway).
    """
    text_features = feat.extract_all_features(parsed_email, claimed_org)
    qr_findings = qr_detector.scan_images_for_qr(parsed_email.get("images", []))
    has_links = len(parsed_email.get("links", [])) > 0
    qr_signal = qr_detector.build_qr_risk_signal(qr_findings, has_visible_links=has_links)

    auth_result = email_auth.check_authentication(raw_email_text or "")
    auth_signal = email_auth.authentication_risk_signal(auth_result)

    sender_history = database.has_seen_sender_before(parsed_email.get("sender"))

    score = 0
    techniques = []

    if text_features["urgency_detected"]:
        score += WEIGHTS["urgency"]
        techniques.append("Urgency Manipulation")

    if text_features["authority_detected"]:
        score += WEIGHTS["authority"]
        techniques.append("Authority Impersonation")

    if text_features["request_detected"]:
        score += WEIGHTS["request"]
        techniques.append("Suspicious Request (money/credentials)")

    if text_features["domain_suspicious"]:
        score += WEIGHTS["domain_suspicious"]
        techniques.append("Sender Domain Mismatch")

    if text_features["suspicious_links_found"]:
        score += WEIGHTS["suspicious_links"]
        techniques.append("Suspicious Link")

    if qr_signal["qr_detected"]:
        score += WEIGHTS["qr_detected"]
        techniques.append("QR Code / Quishing")

    if text_features.get("callback_detected"):
        score += WEIGHTS["callback"]
        techniques.append("Callback Phishing (phone number)")

    if auth_signal["auth_failed"]:
        score += WEIGHTS["auth_failed"]
        techniques.append("Failed Sender Authentication (SPF/DKIM/DMARC)")

    if text_features.get("device_code_phishing_detected"):
        score += WEIGHTS["device_code"]
        techniques.append("Device Code Phishing (OAuth Token Theft)")

    # A brand-new sender only adds risk when OTHER signals already fired --
    # a first-time sender with a perfectly normal email isn't suspicious
    # on its own, but a first-time sender asking for money/urgency is.
    if not sender_history["seen_before"] and techniques:
        score += WEIGHTS["new_sender"]
        techniques.append("First-Time Sender")

    score = min(score, 100)

    # Decide overall attack type based on which signals fired together
    attack_type = classify_attack_type(text_features, qr_signal)

    return {
        "risk_score": score,
        "threat_level": _risk_to_level(score),
        "attack_type": attack_type,
        "techniques_detected": techniques,
        "details": {
            "text_features": text_features,
            "qr_signal": qr_signal,
            "auth_result": auth_result,
            "auth_signal": auth_signal,
            "sender_history": sender_history,
        },
    }


def classify_attack_type(text_features: dict, qr_signal: dict) -> str:
    # Device code phishing uses a REAL login page and steals no password,
    # so it's checked first -- it's a fundamentally different attack
    # (identity/token theft) from the credential-theft patterns below.
    if text_features.get("device_code_phishing_detected"):
        return "Device Code Phishing (OAuth Token Theft)"

    if qr_signal["qr_detected"]:
        return "Quishing (QR Code Phishing)"

    # Whaling: specifically impersonates a senior executive AND asks
    # for something sensitive -- a more targeted, higher-stakes version
    # of BEC.
    if (text_features.get("executive_impersonation_detected")
            and text_features["request_detected"]
            and text_features["domain_suspicious"]):
        return "Whaling (Executive Impersonation)"

    if (text_features["authority_detected"]
            and text_features["request_detected"]
            and text_features["domain_suspicious"]):
        return "Business Email Compromise (BEC)"

    if text_features.get("callback_detected") and text_features["urgency_detected"]:
        return "Callback Phishing"

    if text_features["authority_detected"] or text_features["domain_suspicious"]:
        return "Spear Phishing"

    if text_features["urgency_detected"] or text_features["request_detected"]:
        return "Generic Phishing"

    return "No Clear Threat Detected"


def build_explanation(result: dict) -> str:
    """
    Turns the detection result into a plain-English paragraph explaining
    WHY the email got this score -- this is what the dashboard shows in
    the 'Explanation' panel.
    """
    techniques = result["techniques_detected"]
    attack_type = result["attack_type"]
    qr_signal = result["details"]["qr_signal"]

    if not techniques:
        return "This email does not show any of the common signs of phishing, spear phishing, or QR-code based attacks that this tool checks for."

    reasons = []
    text_features = result["details"]["text_features"]

    if text_features.get("authority_detected"):
        reasons.append("it invokes a position of authority (like a CEO, HR, or IT department) to pressure the reader into acting without question")
    if text_features.get("urgency_detected"):
        reasons.append("it uses urgent, time-pressured language designed to make the reader act before thinking carefully")
    if text_features.get("request_detected"):
        reasons.append("it asks for something sensitive -- money, credentials, or personal/financial information")
    if text_features.get("domain_suspicious"):
        reasons.append(f"the sender's email domain looks suspicious ({text_features.get('reason', 'mismatch detected')})")
    if text_features.get("suspicious_links_found"):
        reasons.append("it contains a link that looks disguised or unusual (e.g. a raw IP address instead of a normal website name)")
    if text_features.get("executive_impersonation_detected"):
        reasons.append("it specifically impersonates a senior executive (like a CEO or CFO), a pattern known as 'whaling'")
    if text_features.get("device_code_phishing_detected"):
        reasons.append(
            "it directs you to a genuine Microsoft/Google/GitHub device-login page and asks you to enter a code -- "
            "this doesn't steal your password, it tricks you into personally authorizing the attacker's device, "
            "handing them a valid access token"
        )
    if text_features.get("callback_detected"):
        reasons.append("it urges the reader to call a phone number, moving the attack to a phone call where normal email safeguards don't apply")
    if result["details"].get("auth_signal", {}).get("auth_failed"):
        reasons.append("the email failed sender authentication checks (SPF/DKIM/DMARC), a strong technical signal that the sender address was spoofed")
    if not result["details"].get("sender_history", {}).get("seen_before", True):
        reasons.append("this is the first time this sender has emailed you")
    if qr_signal.get("qr_detected"):
        reasons.append("it contains a QR code, which attackers use to hide a malicious link from normal email security scanners")

    reason_text = "; ".join(reasons)

    return (
        f"This email was classified as {attack_type} because {reason_text}. "
        f"Together, these signals suggest the email is trying to manipulate the "
        f"reader into acting quickly without verifying the request first."
    )


def _risk_to_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    if score > 0:
        return "LOW"
    return "MINIMAL"


if __name__ == "__main__":
    sample_email = {
        "sender": "ceo.company@gmail.com",
        "subject": "Urgent wire transfer needed",
        "body": "Hi Sarah, as requested by the Finance Department, please "
                "wire transfer $5,000 immediately before 5 PM today.",
        "links": ["http://192.168.1.1/login"],
        "images": [],
    }

    result = analyze_email(sample_email, claimed_org="company")

    print("Risk Score:", result["risk_score"])
    print("Threat Level:", result["threat_level"])
    print("Attack Type:", result["attack_type"])
    print("Techniques Detected:", result["techniques_detected"])
