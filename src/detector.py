"""
detector.py

Combines everything (text features + QR code findings) into one final
result: a risk score, a threat classification, and the list of specific
techniques detected. This is the "brain" that ties parser.py,
features.py, and qr_detector.py together.
"""

from src import features as feat
from src import qr_detector


# How many points each detected signal adds toward the risk score.
# Total is capped at 100.
WEIGHTS = {
    "urgency": 20,
    "authority": 20,
    "request": 20,
    "domain_suspicious": 25,
    "suspicious_links": 20,
    "qr_detected": 25,
}


def analyze_email(parsed_email: dict, claimed_org: str = None) -> dict:
    """
    Takes a parsed email (from parser.py) and returns the full
    detection result: risk score, threat level, techniques found,
    and which signals contributed.
    """
    text_features = feat.extract_all_features(parsed_email, claimed_org)
    qr_findings = qr_detector.scan_images_for_qr(parsed_email.get("images", []))
    has_links = len(parsed_email.get("links", [])) > 0
    qr_signal = qr_detector.build_qr_risk_signal(qr_findings, has_visible_links=has_links)

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
        },
    }


def classify_attack_type(text_features: dict, qr_signal: dict) -> str:
    if qr_signal["qr_detected"]:
        return "Quishing (QR Code Phishing)"

    if (text_features["authority_detected"]
            and text_features["request_detected"]
            and text_features["domain_suspicious"]):
        return "Business Email Compromise (BEC)"

    if text_features["authority_detected"] or text_features["domain_suspicious"]:
        return "Spear Phishing"

    if text_features["urgency_detected"] or text_features["request_detected"]:
        return "Generic Phishing"

    return "No Clear Threat Detected"


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
